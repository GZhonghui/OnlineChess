import queue
import socket
import threading

import server_lib.worker.command_pool as cp
import server_lib.worker.client_manager as cm
import server_lib.worker.tcp_message_pool as mp

import server_lib.server as server

class SendThread(threading.Thread):

    def __init__(self,client_connection):
        super().__init__()

        self.client_connection=client_connection

        self.tcp_connection=client_connection.tcp_connection

        self.message_pool=client_connection.tcp_message_pool

    def __del__(self):
        pass

    def run(self):
        
        try:
            while True:
                message=self.message_pool.get_message()

                if message.message_type==-1:
                    raise BaseException()

                elif message.message_type==6:
                    another=self.client_connection.father.get_name(self.client_connection.another)

                    send_type=3
                    send_type=send_type.to_bytes(1,byteorder='big',signed=False)

                    another=another.encode('utf-8')

                    send_len=len(another)
                    send_len=send_len.to_bytes(1,byteorder='big',signed=False)

                    send_all=send_type+message.message+send_len+another

                    self.tcp_connection.sendall(send_all)

                else:
                    self.tcp_connection.sendall(message.get_bytes())

        except:
            if not self.client_connection.submited():
                self.client_connection.submit()

class ReceiveThread(threading.Thread):

    def __init__(self,client_connection):
        super().__init__()

        self.client_connection=client_connection

        self.id=client_connection.id
        self.tcp_connection=client_connection.tcp_connection

        self.command_pool=client_connection.command_pool

    def __del__(self):
        pass

    def run(self):

        try:
            while True:
                recv_type=self.tcp_connection.recv(1)
                if len(recv_type)==0:
                    raise BaseException()

                recv_type=int.from_bytes(recv_type,byteorder='big',signed=False)

                if recv_type==0:
                    self.command_pool.push_command(cp.Command(0,self.id))

                elif recv_type==1:
                    recv_len=self.tcp_connection.recv(1)
                    recv_len=int.from_bytes(recv_len,byteorder='big',signed=False)

                    recv_message=self.tcp_connection.recv(recv_len)
                    recv_message=recv_message.decode('utf-8')

                    self.client_connection.set_name(recv_message)

                elif recv_type==2:
                    movement=self.tcp_connection.recv(4)
                    self.command_pool.push_command(cp.Command(2,movement,self.id))

        except:
            if not self.client_connection.submited():
                self.client_connection.submit()

class ClientConnection():

    def __init__(self,server_handle:server.ServerHandle,id,tcp_connection):
        self.__submited_for_deleted=False
        self.__submited_for_deleted_lock=threading.Lock()

        self.father=server_handle

        self.id=id

        self.tcp_connection=tcp_connection

        self.submit_end=server_handle.delete_pool

        self.command_pool=server_handle.command_pool

        self.tcp_message_pool=mp.TCP_MessagePool()

        self.send_thread=SendThread(self)
        self.receive_thread=ReceiveThread(self)

        self.__user_name=None
        self.__user_name_lock=threading.Lock()
        self.__user_name_semaphore=threading.Semaphore(0)

    def __del__(self):
        pass

    def ready(self):
        self.__user_name_semaphore.acquire()
        
        name=self.get_name()

        self.__user_name_semaphore.release()

        return name

    def set_name(self,name:str):
        self.__user_name_lock.acquire()

        self.__user_name=name

        self.__user_name_lock.release()

        self.__user_name_semaphore.release()

        print(self.id,'reged',name)

    def get_name(self):
        self.__user_name_lock.acquire()

        res_name=self.__user_name

        self.__user_name_lock.release()

        return res_name

    def notify_matched(self,order:int,id:int):
        self.another=id

        self.send_message(mp.TCP_Message(6,order.to_bytes(1,byteorder='big',signed=False)))

    def send_message(self,message:mp.TCP_Message):
        self.tcp_message_pool.send_message(message)

    def submited(self):
        self.__submited_for_deleted_lock.acquire()

        res=self.__submited_for_deleted

        self.__submited_for_deleted_lock.release()

        return res

    def submit(self):
        self.__submited_for_deleted_lock.acquire()

        self.__submited_for_deleted=True

        self.__submited_for_deleted_lock.release()

        self.submit_end.submit(self.id)

    def disconnect(self):
        try:
            self.tcp_connection.close()
        except:
            pass

        self.tcp_message_pool.send_message(mp.TCP_Message(-1,None))

    def wait_for_end(self):
        if self.send_thread.isAlive():
            self.send_thread.join()

        if self.receive_thread.isAlive():
            self.receive_thread.join()

    def run(self):
        self.send_thread.start()
        self.receive_thread.start()