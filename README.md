# dummysocks

Simple forwarding SOCKS proxy server

When using a proxy server only occasionally, for instance to create a tunnel to
a university network, or to route sensitive traffic over the TOR network, the
simulataneous steps of activating the server and configuring the browser to
make use of it, followed by deactivating the server and reverting the browser
to direct internet access, is cumbersome. Dummysocks solves this annoyance by
providing a SOCKS service for direct internet access so that the browser
configuration can be left unchanged.


## usage

In the web browser set the proxy server to SOCKS version 5 and any port >1024.
In this example we use 9050. Then open a terminal and run:

    $ dummysocks 9050

The server should start with the message "initializing dummysocks on port
9050...OK" and continue logging any internet traffic passing through it on a
line per line basis.

To change from direct internet to an SSH tunnel kill it by pressing ^C and
execute:

    $ ssh -D localhost:9050 [remotehost] -N

To change to the TOR network compile and execute the [tor proxy
server](https://gitweb.torproject.org/tor.git), which operates on port 9050 by
default:

    $ tor

This will give access to .onion links and thwart ISP monitoring. Note that this
practice is [strongly advised
against](https://www.torproject.org/docs/faq.html.en#TBBOtherBrowser) by the
TOR project, which recommends the
[torbrowser](https://www.torproject.org/projects/torbrowser.html.en) as the
only secure means of accessing the network.


## installation

Dummysocks does not have any dependencies other than Python3.5 and can be run
directly from the /bin directory. Alternatively it can be installed system wide
using Python's setuptools:

    python3 setup.py install

Or in ~/.local/bin:

    python3 setup.py install --user
