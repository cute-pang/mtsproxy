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
	            normal_node.sockfd = connection.fileno()
	            normal_node.node_type = NODE_TYPE_NORMAL_CLIENT

	            #注册epoll事件
	            epoll.register(connection.fileno(), select.EPOLLIN)
	            node[connection.fileno()] = normal_node

	         elif event & select.EPOLLIN:
	         	#接受到请求数据
	         	tmp_node = node[fileno]
	         	tmp_data += node[fileno].conn.recv(1024)

	         	tmp_node.flow = flow()
	         	#根据tmp_data初始化节点流量
	            if 'GET' in tmp_data:
	            	tmp_node.down_flow = tmp_data
                    tmp_node.handle_flow()
                    
	         elif event & select.EPOLLOUT:
	            byteswritten = connections[fileno].send(responses[fileno])
	            responses[fileno] = responses[fileno][byteswritten:]
	            if len(responses[fileno]) == 0:
	               epoll.modify(fileno, 0)
	               connections[fileno].shutdown(socket.SHUT_RDWR)
	         elif event & select.EPOLLHUP:
	            epoll.unregister(fileno)
	            connections[fileno].close()
	            del connections[fileno]
                
                
	finally:
	   epoll.unregister(ssock.fileno())
	   epoll.close()
	   ssock.close()
		