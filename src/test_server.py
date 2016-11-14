from pub import *

import socket

tcpCliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

tcpCliSock.bind(('127.0.0.1', HTTPS_PROT))
tcpCliSock.listen(1)

while True:
	ss, addr = tcpCliSock.accept()
	try:
		while True:
			str = ss.recv(1024)
			print str
			ss.send("Hello world message comes from loopback server.!")
	finally:
		ss.close()
