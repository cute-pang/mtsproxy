# -*- coding: utf-8 -*- 

from pub import *
import socket, select, threading, time

g_send_list = []
g_recv_list = []

send_mutex = threading.Lock()
recv_mutex = threading.Lock()

def send_worker(send_sock):
    if send_mutex.acquire(1):
        while index in range(0, len(g_send_list)):
            req = g_send_list.pop()
            send_sock.send(req)
        send_mutex.release()
    time.sleep(1)

def recv_worker():
    if recv_mutex.acquire(1):
        while index in range(0, len(g_recv_list)):
            rsp = g_recv_list.pop()
            #TODO将response送回最开始的client端
        recv_mutex.release()
    time.sleep(1)

def client_send_thread_init():
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    send_sock.connect(('127.0.0.1', 8082))
    worker = threading.Thread(target=send_worker, args=(send_sock,))
    worker.start()

def client_recv_thread_init():
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    lsock.bind(('127.0.0.1', 8081))
    lsock.listen(5)
    lsock.setblocking(0)
    epoll.register(lsock.fileno(), select.EPOLLIN)

    try:
        recv_sock = None
        sock_has_build = False
        while True:
            events = epoll.poll(1)
            for fileno, event in events:
                if (fileno == lsock.fileno()) and (False == sock_has_build):
                    connection, address = lsock.accept()
                    recv_sock = connection
                    recv_sock.setblocking(0)

                    #注册epoll事件
                    epoll.register(recv_sock.fileno(), select.EPOLLIN)
                    worker = threading.Thread(target=send_worker)
                    worker.start()
                    sock_has_build = True
                elif event & select.EPOLLIN:
                    if fileno == recv_sock.fileno():
                        data = recv_sock.recv(1024)
                        if len(data) == 0:
                            continue

                        #TODO解析data，将其装换为response
                        response = data
                        if recv_mutex.acquire(1):
                            #将response送添加到发送链表
                            g_recv_list.append(response)
                            recv_mutex.release()
    finally:
       epoll.unregister(lsock.fileno())
       epoll.close()
       lsock.close()


def main_loop():
    EOL1 = b'\n\n'
    EOL2 = b'\n\r\n'

    ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ssock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    ssock.bind(('127.0.0.1', 8080))
    ssock.listen(5)
    ssock.setblocking(0)

    epoll.register(ssock.fileno(), select.EPOLLIN)
    try:
        while True:
            events = epoll.poll(1)
            for fileno, event in events:
                if fileno == ssock.fileno():
                    #建立连接
                    connection, address = ssock.accept()
                    connection.setblocking(0)

                    #注册epoll事件
                    epoll.register(connection.fileno(), select.EPOLLIN)
            
                elif event & select.EPOLLIN:
                    #TODO找到对应的接受数据的sock
                    data = g_node[fileno].conn.recv(1010)
                    #连接被关闭
                    if (len(data) == 0):
                        continue

                    #TODO将数据转化成request
                    request = data

                    #将数据添加到发送链表
                    if send_mutex.acquire(1):
                        #将response送添加到发送链表
                        g_send_list.append(request)
                        send_mutex.release()

    finally:
        epoll.unregister(ssock.fileno())
        epoll.close()
        ssock.close()

if __name__ == "__main__":
    client_send_thread_init()
    client_recv_thread_init()
    main_loop()