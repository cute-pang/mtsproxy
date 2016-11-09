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
				
		