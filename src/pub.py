# -*- coding: utf-8 -*- 
import socket, select

GLOBAL_PROXY_PORT = 8080
PROXY_SERVER_IP = '23.83.226.130'
PROXY_SERVER_PORT = 8080

HTTPS_PROT = 443

NODE_TYPE_NORMAL_CLIENT = 0
NODE_TYPE_NORMAL_SERVER = 1
NODE_TYPE_PROXY_CLIENT = 2
NODE_TYPE_PROXY_SERVER = 3

#全局node列表
node = {}
#全局epoll
epoll = select.epoll()

def connect_to_remote(ip, port, need_warp):
    tcpCliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpCliSock.settimeout(timeout)

    if not need_warp:
        tcpCliSock.connect((ip, port))
        return tcpCliSock
    
    #封装成ssl socket
    sock = ssl.wrap_socket(tcpCliSock)
    try:
        sock.connect((ip, port))
    except socket.timeout:
        #连接超时处理
        sock.close()
        sys.exit()
    return sock
'''
    #发送并接收数据
    sock.sendall(data)
    fp = sock.makefile('rb', 0)
    #读取http response状态
    status = fp.readline(line_len).split()[1]
'''

#节点类,用于传输上行或者下行流量
class node():
	def __init__(self):
		#上行/下行描述符，如果为-1，则使用sockfd收发数据
		self.upward_fd = -1
		self.downward_fd = -1
		self.sockfd = -1

		#设置节点收发缓冲区
		self.down_flow = None
		self.up_flow = None
        
        self.node_type = -1

	def handle_flow(self):
        #没有数据
        if self.flow is None:
            pass
            
        #如果是普通的客户端节点
		if self.node_type is NODE_TYPE_NORMAL_CLIENT:
            #处理上行流量
			if self.up_flow is not None:
				self.sockfd.send(self.up_flow.data)
                self.up_flow = None
			
            #处理下行流量
            if self.down_flow is not None:
				if self.downward_fd == -1:
                    sock = connect_to_remote(PROXY_SERVER_IP, PROXY_SERVER_PORT, FALSE)
                    tmp_sk_fd = sock.fileno()
                    #初始化代理node
                    node[tmp_sk_fd] = node()
                    node[tmp_sk_fd].upward_fd = self.sockfd
                    node[tmp_sk_fd].sockfd = tmp_sk_fd
                    node[tmp_sk_fd].node_type = NODE_TYPE_NORMAL_SERVER
                    self.downward_fd = tmp_sk_fd
                    epoll.register(tmp_sk_fd, select.EPOLLIN)
                #拷贝数据，触发pollin事件
                node[self.downward_fd].down_flow = self.down_flow    
                epoll.modify(tmp_sk_fd, select.EPOLLIN)
                self.down_flow = None
		
        #如果是普通的服务端节点
        if self.node_type is NODE_TYPE_NORMAL_SERVER:
            #处理下行流量
			if self.down_flow is not None:
				self.sockfd.send(self.down_flow)
                self.down_flow = None
			if self.up_flow is not None:
                node[self.upward_fd].up_flow = self.up_flow
                epoll.modify(self.upward_fd, select.EPOLLOUT)
            
        #如果是代理节点客户端
        if self.node_type is NODE_TYPE_PROXY_CLIENT:
            #处理上行流量
			if self.up_flow is not None:
				self.sockfd.send(self.up_flow.data)
                self.up_flow = None
            #处理下行流量
            if self.down_flow is not None：
                if self.downward_fd == -1:
                    sock = connect_to_remote(HOST, HTTPS_PROT, TRUE)
                    tmp_sk_fd = sock.fileno()
                    #初始化代理node
                    node[tmp_sk_fd] = node()
                    node[tmp_sk_fd].upward_fd = self.sockfd
                    node[tmp_sk_fd].sockfd = tmp_sk_fd
                    node[tmp_sk_fd].node_type = NODE_TYPE_PROXY_SERVER
                    self.downward_fd = tmp_sk_fd
                    epoll.register(tmp_sk_fd, select.EPOLLIN)
                #拷贝数据，触发pollin事件
                node[self.downward_fd].down_flow = self.down_flow    
                epoll.modify(tmp_sk_fd, select.EPOLLIN)
                self.down_flow = None        
        
        #如果是代理节点服务端
        if self.node_type is NODE_TYPE_PROXY_SERVER:
            #处理下行流量
			if self.down_flow is not None:
				self.sockfd.send(self.down_flow)
                self.down_flow = None
			if self.up_flow is not None:
                node[self.upward_fd].up_flow = self.up_flow
                epoll.modify(self.upward_fd, select.EPOLLOUT) 
				
	def handle_close(self):
        if self.epoll is None:
            return 
        else:
            self.epoll.unregister(self.sockfd)
            if (self.node_type == NODE_TYPE_NORMAL_CLIENT) or (self.node_type == NODE_TYPE_PROXY_CLIENT):
                self.epoll.modify(self.downward_fd, select.EPOLLHUP)
            self.sockfd.close()
            del node[self.sockfd]
            
    def resolve_dns(self):
        #先用最简单的方式，可以扩展
        return socket.gethostby_name(self.flow.host)
        
        