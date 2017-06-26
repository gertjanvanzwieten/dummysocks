#! /usr/bin/python3

import asyncio


async def copy_stream(id, reader, writer, bufsize=1<<16):
  '''copy all data from reader to writer'''

  try:
    data = await reader.read(bufsize)
    while data:
      print(id, len(data), 'bytes')
      await writer.drain()
      writer.write(data)
      data = await reader.read(bufsize)
    writer.close()
  except Exception as e:
    print(id, 'error:', e)
  else:
    print(id, 'closed')


async def socksfwd(reader, writer):
  '''implement socks protocol, upon success open remote reader/writer'''

  version, nauth = await reader.readexactly(2)
  if version != 5:
    print( 'ERROR: wrong protocol' )
    writer.close()
    return

  auth_methods = tuple(await reader.readexactly(nauth))
  if 0 not in auth_methods:
    print( 'ERROR: no acceptable authentication method' )
    writer.write(b'\x05\xff') # no acceptable authentication method
    writer.close()
    return

  # select no authentication
  writer.write(b'\x05\x00')

  version, command, nil, addrtype = await reader.readexactly(4)
  if version != 5 or command not in (1,2,3) or nil != 0:
    print('ERROR: protocol error')
    writer.write(b'\x05\x07') # command not supported / protocol error
    writer.close()
    return

  if addrtype == 1:
    destbytes = await reader.readexactly(4)
    host = '.'.join(str(n) for n in destbytes)
  elif addrtype == 3:
    n, = await reader.readexactly(1)
    hostbytes = await reader.readexactly(n)
    destbytes = bytes([n]) + hostbytes
    host = hostbytes.decode()
  elif addrtype == 4:
    destbytes = await reader.readexactly(16)
    hosthex = destbytes.hex()
    assert len(hosthex) == 32
    host = ':'.join(hexhost[i*4:(i+1)*4].lstrip('0') or '0' for i in range(8))
  else:
    print( 'ERROR: address type not supported' )
    writer.write(b'\x05\x08') # address type not supported
    writer.close()
    return

  portbytes = await reader.readexactly(2)
  portmajor, portminor = portbytes
  port = (portmajor<<8) + portminor

  print('{}:{} -- connecting'.format(host,port))

  try:
    remote_reader, remote_writer = await asyncio.open_connection(host, port)
  except Exception as e:
    print('ERROR: failed to connect to {}:{}: {}'.format(host,port,e))
    writer.write(b'\x05\x04') # host unreachable
    writer.close()
    return

  # request granted
  writer.write(bytes([5,0,0,addrtype])+destbytes+portbytes)

  asyncio.ensure_future(copy_stream('{}:{} <-'.format(host,port), reader, remote_writer))
  asyncio.ensure_future(copy_stream('{}:{} ->'.format(host,port), remote_reader, writer))
