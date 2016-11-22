from pub import *
import time

import socket

tc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tc.settimeout(10) 

tc.connect(('127.0.0.1', GLOBAL_LOCAL_PROT))


tc.send("Http request from test client!" + str(time.time()))
recv_str = tc.recv(1024)
print recv_str

tc.shutdown(socket.SHUT_RDWR)
tc.close()