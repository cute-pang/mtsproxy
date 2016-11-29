
import socket,time

tcpCliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

tcpCliSock.bind(('127.0.0.1', 8085))
tcpCliSock.listen(5)

while True:
    try:
        ss, addr = tcpCliSock.accept()
        str = ss.recv(1024)
        print str
        ss.send("Hello world message comes from loopback server.!")
        time.sleep(10)
        ss.close()
    except:
        pass
