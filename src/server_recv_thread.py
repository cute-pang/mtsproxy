# -*- coding: utf-8 -*-
import socket, select, threading, time
from server import recv_mutex, g_server_recv_list, g_fd_map2_request,g_fd_map2_sock
from global_param import g_epoll

def recv_worker():
    while True:
        if recv_mutex.acquire(1):
            for index in range(0, len(g_server_recv_list)):
                request = g_server_recv_list.pop()
                #根据request，发起连接，并在g_epoll中注册EPOLLIN
                tc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tc.connect(('127.0.0.1', 8085))
                g_fd_map2_request[tc.fileno()] = request
                g_fd_map2_sock[tc.fileno()] = tc
                g_epoll.register(tc.fileno(), select.EPOLLIN)
                tc.send(request[5:])
            recv_mutex.release()
        time.sleep(1)

def server_recv_thread_init():
    epoll = select.epoll()
    g_server_listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    g_server_listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    g_server_listen_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    g_server_listen_sock.bind(('127.0.0.1', 8082))
    g_server_listen_sock.listen(5)
    g_server_listen_sock.setblocking(0)
    epoll.register(g_server_listen_sock.fileno(), select.EPOLLIN)

    try:
        recv_sock = None
        sock_has_build = False
        while True:
            events = epoll.poll(1)
            for fileno, event in events:
                if (fileno == g_server_listen_sock.fileno()) and (False == sock_has_build):
                    connection, address = g_server_listen_sock.accept()
                    recv_sock = connection
                    recv_sock.setblocking(0)

                    #注册epoll事件
                    epoll.register(recv_sock.fileno(), select.EPOLLIN)
                    worker = threading.Thread(target = recv_worker)
                    worker.start()
                    sock_has_build = True
                elif event & select.EPOLLIN:
                    if fileno == recv_sock.fileno():
                        data = recv_sock.recv(1024)
                        if len(data) == 0:
                            continue

                        if recv_mutex.acquire(1):
                            #将response送添加到发送链表
                            g_server_recv_list.append(data)
                            recv_mutex.release()
    finally:
        epoll.unregister(g_server_listen_sock.fileno())
        epoll.close()
        g_server_listen_sock.close()

if __name__ == "__main__":
    server_recv_thread_init()