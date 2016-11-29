# -*- coding: utf-8 -*-
import socket, select, threading, time
from client import recv_mutex, g_recv_list, g_fd_map2_cli_sock

def recv_worker():
    while True:
        if recv_mutex.acquire(1):
            for index in range(0, len(g_recv_list)):
                rsp = g_recv_list.pop()
                #TODO将response送回最开始的client端
                fd = int(rsp[:5])
                data = rsp[5:]
                g_fd_map2_cli_sock[fd].send(data)
            recv_mutex.release()
        time.sleep(1)

def client_recv_thread_init():
    epoll = select.epoll()
    g_client_listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    g_client_listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    g_client_listen_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    g_client_listen_sock.bind(('127.0.0.1', 8081))
    g_client_listen_sock.listen(5)
    g_client_listen_sock.setblocking(0)
    epoll.register(g_client_listen_sock.fileno(), select.EPOLLIN)

    try:
        recv_sock = None
        sock_has_build = False
        while True:
            events = epoll.poll(1)
            for fileno, event in events:
                if (fileno == g_client_listen_sock.fileno()) and (False == sock_has_build):
                    connection, address = g_client_listen_sock.accept()
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

                        #添加到接受队列
                        if recv_mutex.acquire(1):
                            #将response送添加到发送链表
                            g_recv_list.append(data)
                            recv_mutex.release()
    finally:
       epoll.unregister(g_client_listen_sock.fileno())
       epoll.close()
       g_client_listen_sock.close()

if __name__ == "__main__":
    client_recv_thread_init()