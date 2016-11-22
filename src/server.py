# -*- coding: utf-8 -*- 

from pub import *
import socket, select

def main_loop():
    EOL1 = b'\n\n'
    EOL2 = b'\n\r\n'

    ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ssock.bind((PROXY_SERVER_IP, PROXY_SERVER_PORT))
    ssock.listen(5)
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
                    normal_node.node_type = NODE_TYPE_PROXY_CLIENT

                    #注册epoll事件
                    epoll.register(connection.fileno(), select.EPOLLIN)
                    g_node[connection.fileno()] = normal_node

                elif event & select.EPOLLHUP:
                    print 'server abc'
                    g_node[fileno].handle_close()
            
                elif event & select.EPOLLIN:
                    data = g_node[fileno].conn.recv(1024)
                
                    if g_node[fileno].node_type is NODE_TYPE_PROXY_CLIENT:
                        g_node[fileno].down_flow = data
                    elif g_node[fileno].node_type is NODE_TYPE_PROXY_SERVER:
                        g_node[fileno].up_flow = data
                
                    g_node[fileno].handle_flow()
                    
                elif event & select.EPOLLOUT:
                    g_node[fileno].handle_flow()
                
    finally:
       epoll.unregister(ssock.fileno())
       epoll.close()
       ssock.close()

main_loop() 