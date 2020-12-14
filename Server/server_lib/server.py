import threading
import socket
import queue

import server_lib.worker.client_connection as cc
import server_lib.worker.client_manager as cm
import server_lib.worker.command_pool as cp

class ID_Recoder():

    def __init__(self,size:int):
        self.id_pool=queue.Queue(size)
        self.id_pool_lock=threading.Lock()
        self.id_pool_semaphore=threading.Semaphore(size)

        for i in range(size):
            self.id_pool.put(i)

    def __del__(self):
        pass

    def get_id(self):
        self.id_pool_semaphore.acquire()

        self.id_pool_lock.acquire()

        res_id=self.id_pool.get()

        self.id_pool_lock.release()
        
        return res_id

    def return_id(self,x:int):
        self.id_pool_lock.acquire()

        self.id_pool.put(x)

        self.id_pool_lock.release()

        self.id_pool_semaphore.release()

class ServerHandle():

    def __init__(self,ip:str,port=12346):
        self.user_limit=20

        self.ip=ip
        self.port=port

        self.tcp_server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        self.id_pool=ID_Recoder(self.user_limit)

        self.command_pool=cp.CommandPool()
        self.command_pool_thread=cp.ProcessCommandPoolThread(self)

        self.delete_pool=cm.SubmitForDelete()
        self.client_manager=cm.ClientManager(self)

        self.clients=dict()
        self.clients_lock=threading.Lock()

        self.another=dict()
        self.another_lock=threading.Lock()

        self.waiting_queue=list()

    def __del__(self):
        pass

    def get_name(self,id):
        self.clients_lock.acquire()

        ask=self.clients[id]

        self.clients_lock.release()

        return ask.ready()

    def make_pair(self,x,y):
        self.another_lock.acquire()

        self.another[x]=y
        self.another[y]=x

        self.another_lock.release()

    def run(self):
        
        print('Server thread start')

        self.command_pool_thread.start()
        self.client_manager.start()

        self.tcp_server.bind((self.ip,self.port))

        print('Start listen')

        self.tcp_server.listen(self.user_limit)

        try:
            while True:
                next_id=self.id_pool.get_id()

                client,client_address=self.tcp_server.accept()

                print(next_id,': Connection from',client_address)

                self.clients_lock.acquire()

                self.clients[next_id]=cc.ClientConnection(self,next_id,client)
                self.clients[next_id].run()

                self.clients_lock.release()

                if not len(self.waiting_queue):
                    self.waiting_queue.append(next_id)

                else:
                    self.make_pair(self.waiting_queue[0],next_id)

                    self.clients_lock.acquire()

                    self.clients[next_id].notify_matched(self.waiting_queue[0])
                    self.clients[self.waiting_queue[0]].notify_matched(next_id)

                    self.clients_lock.release()

                    self.waiting_queue.clear()
        
        except: 
            self.command_pool_thread.push_shutdown_command()

            if self.command_pool_thread.isAlive():
                self.command_pool_thread.join()

            self.client_manager.push_shutdown_command()

            if self.client_manager.isAlive():
                self.client_manager.join()

        print('Clean')