# -*- coding: utf-8 -*- 

GLOBAL_PROXY_PORT = 8080
PROXY_SERVER_IP = '23.83.226.130'
PROXY_SERVER_PORT = 8080

NODE_TYPE_NORMAL_CLIENT = 0
NODE_TYPE_NORMAL_SERVER = 1
NODE_TYPE_PROXY_CLIENT = 2
NODE_TYPE_PROXY_SERVER = 3

#全局node列表
node = {}

#流量类，分为上行流量和下行流量
class flow():
	def __init__(self):
		self.is_down_flow = False
		self.data = None


#节点类,用于传输上行或者下行流量
class node():
	def __init__(self):
		#上行/下行描述符，如果为-1，则使用sockfd收发数据
		self.upward_fd = -1
		self.downward_fd = -1

		self.sockfd = -1
		self.conn = None
		self.flow = None

		#设置节点收发缓冲区
		self.snd_buf = None
		self.rcv_buf = None
        
        self.node_type = -1

	def handle_flow(self):
        #没有数据
        if self.flow is None:
            pass
            
        #如果是普通的客户端节点
		if self.node_type is NODE_TYPE_NORMAL_CLIENT:
			if self.downward_fd == -1:
				self.sockfd.send(self.flow.data)
			else:
				write(self.downward_fd, self.flow.data)
		
        #如果是普通的服务端节点
        if self.node_type is NODE_TYPE_NORMAL_SERVER:
			if self.upward_fd == -1:
				self.sockfd.recv(self.flow.data)
			else:
            
        #如果是代理节点客户端
        if self.node_type is NODE_TYPE_PROXY_CLIENT:
            pass
            
        
        #如果是代理节点服务端
        if self.node_type is NODE_TYPE_PROXY_SERVER:
            pass
				


def main_loop():
	EOL1 = b'\n\n'
	EOL2 = b'\n\r\n'

	ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ssock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	ssock.bind(('0.0.0.0', GLOBAL_PROXY_PORT))
	ssock.listen(1)
	ssock.setblocking(0)
	ssock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

	epoll = select.epoll()
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
	            normal_node.conn = connection

	            #注册epoll事件
	            epoll.register(connection.fileno(), select.EPOLLIN)
	            node[connection.fileno()] = normal_node

	         elif event & select.EPOLLIN:
	         	#接受到请求数据
	         	tmp_node = node[fileno]
	         	tmp_data = node[fileno].conn.recv(1024)

	         	tmp_node.flow = flow()
	         	#根据tmp_data初始化节点流量
	            if 'GET' in tmp_data and 'Host' in tmp_data:
	            	tmp_node.flow.is_down_flow = True
	            	tmp_node.flow.data = tmp_data

	            	#如果下行fd还没有创建，则创建
	            	if tmp_node.downward_fd == -1:
	            		sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	            		sk.connect((PROXY_SERVER_IP, PROXY_SERVER_PORT))
	            		tmp_node.downward_fd = sk.fileno()
	           	else:
	           		tmp_node.flow.is_down_flow = False
	           		tmp_node.flow.data = tmp_data

	           		#如果是上行流量，但是上行fd为-1，则创建
	           		if tmp_node.upward_fd == -1:
	           			sk = 

	                

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
		