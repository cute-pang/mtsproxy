from pub import *

import socket

tcpCliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

tcpCliSock.bind(('127.0.0.1', HTTPS_PROT))
tcpCliSock.listen(5)

while True:
    try:
        ss, addr = tcpCliSock.accept()
        str = ss.recv(1024)
        print str
        ss.send("Hello world message comes from loopback server.!")
        ss.close()
    except:
        pass
