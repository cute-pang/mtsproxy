# -*- coding: utf-8 -*-
import socket, select, threading, time
from global_param import g_epoll

send_mutex = threading.Lock()
recv_mutex = threading.Lock()

g_server_recv_list = []
g_server_send_list = []

g_fd_map2_request = {}
g_fd_map2_sock = {}

def send_worker(send_sock):
    while True:
        if send_mutex.acquire(1):
            for index in range(0, len(g_server_send_list)):
                rsp = g_server_send_list.pop()
                send_sock.send(rsp)
            send_mutex.release()
        time.sleep(1)

def server_send_thread_init():
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    send_sock.connect(('127.0.0.1', 8081))
    worker = threading.Thread(target=send_worker, args=(send_sock,))
    worker.start()

def main_loop():
    try:
        while True:
            events = g_epoll.poll(1)
            for fileno, event in events:
                if event & select.EPOLLIN:
                    for key in g_fd_map2_request.keys():
                        print g_fd_map2_request[key]
                    data = g_fd_map2_sock[fileno].recv(1010)

                    #连接被关闭
                    if (len(data) == 0):
                        continue

                    #TODO构造response数据
                    request = g_fd_map2_request[fileno]
                    response = "%s%s"%(request[:5], data)
                    if send_mutex.acquire(1):
                        #将response送添加到发送链表
                        g_server_send_list.append(response)
                        send_mutex.release()
    finally:
       g_epoll.close()

if __name__ == "__main__":
    server_send_thread_init()
    main_loop()