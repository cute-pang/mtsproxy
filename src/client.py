# -*- coding: utf-8 -*- 

from pub.py import *
import socket, select

def main_loop():
	EOL1 = b'\n\n'
	EOL2 = b'\n\r\n'

	ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ssock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	ssock.bind(('0.0.0.0', GLOBAL_PROXY_PORT))
	ssock.listen(1)
	ssock.setblocking(0)
	ssock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

	epoll.register(ssock.fileno(), select.EPOLLIN)

	try:
	   while True:
            events = epoll.poll(1)
            for fileno, event in events:
                if fileno == ssock.fileno():
                #建立连接
                connection, address = ssock.accept()
                connection.setblocking(0)

                #初始化节点
                normal_node = node()
                normal_node.conn = connection
                normal_node.node_type = NODE_TYPE_NORMAL_CLIENT

                #注册epoll事件
                epoll.register(connection.fileno(), select.EPOLLIN)
                node[connection.fileno()] = normal_node

                elif event & select.EPOLLHUP:
                    node[fileno].handle_close()
                
                elif event & select.EPOLLIN:
                    data += node[fileno].conn.recv(1024)

                    if node[fileno].node_type is NODE_TYPE_NORMAL_CLIENT:
                        node[fileno].down_flow += data
                    elif node[fileno].node_type is NODE_TYPE_NORMAL_SERVER:
                        node[fileno].up_flow += data

                node[fileno].handle_flow()
                    
                elif event & select.EPOLLOUT:
                    node[fileno].handle_flow()           
                
	finally:
	   epoll.unregister(ssock.fileno())
	   epoll.close()
	   ssock.close()
		