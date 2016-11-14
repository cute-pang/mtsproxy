from pub import *

import socket

tc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tc.settimeout(10) 

tc.connect(('127.0.0.1', GLOBAL_LOCAL_PROT))

tc.send("Http request from test client!")

try:
    print tc.recv(48)
		
finally:
    tc.close()