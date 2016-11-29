# -*- coding: utf-8 -*-
import socket, select, threading, time

g_send_list = []
g_recv_list = []
g_fd_map2_cli_sock = {}
send_mutex = threading.Lock()
recv_mutex = threading.Lock()

def send_worker(send_sock):
    while True:
        if send_mutex.acquire(1):
            for index in range(0, len(g_send_list)):
                req = g_send_list.pop()
                send_sock.send(req)
            send_mutex.release()
        time.sleep(1)

def client_send_thread_init():
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    send_sock.connect(('127.0.0.1', 8082))
    worker = threading.Thread(target=send_worker, args=(send_sock,))
    worker.start()

def main_loop():
    EOL1 = b'\n\n'
    EOL2 = b'\n\r\n'

    epoll = select.epoll()
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
                    g_fd_map2_cli_sock[connection.fileno()] = connection
            
                elif event & select.EPOLLIN:
                    #TODO找到对应的接受数据的sock
                    data = g_fd_map2_cli_sock[fileno].recv(1010)
                    #连接被关闭
                    if (len(data) == 0):
                        continue

                    #将数据转化成request
                    request = "%5d%s"%(fileno, data)

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
    main_loop()