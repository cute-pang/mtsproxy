from pub import *

import socket

tcpCliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpCliSock.settimeout(10) 

tcpCliSock.connect(('127.0.0.1', GLOBAL_LOCAL_PROT))
tcpCliSock.listen(1)

tcpCliSock.send("Http request from test client!")

while True:
	try:
		str = ss.recv(1024)
		print str
	finally:
		ss.close()