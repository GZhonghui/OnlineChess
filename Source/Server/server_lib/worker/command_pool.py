import queue
import threading

import server_lib.worker.tcp_message_pool as mp

import server_lib.server as server

class Command():

    def __init__(self,command_type:int,command:bytes,submit_user:int):
        self.command_type=command_type
        self.command=command
        self.submit_user=submit_user

    def __del__(self):
        pass

class CommandPool():
    
    def __init__(self):
        self.pool=queue.Queue()
        self.pool_lock=threading.Lock()
        self.pool_semaphore=threading.Semaphore(0)

    def __del__(self):
        pass

    def push_command(self,command:Command):
        self.pool_lock.acquire()

        self.pool.put(command)

        self.pool_lock.release()

        self.pool_semaphore.release()

    def get_command(self):
        self.pool_semaphore.acquire()

        self.pool_lock.acquire()

        latest_command=self.pool.get()

        self.pool_lock.release()

        return latest_command

class ProcessCommandPoolThread(threading.Thread):

    def __init__(self,server_handle:server.ServerHandle):
        super().__init__()

        self.server_handle=server_handle
        self.command_pool=server_handle.command_pool

    def __del__(self):
        pass

    def push_shutdown_command(self):
        self.command_pool.push_command(Command(-1,None,None))

    def run(self):
        
        while True:
            latest_command=self.command_pool.get_command()

            if latest_command.command_type==-1:
                break

            elif latest_command.command_type==0:
                self.server_handle.delete_pool.submit(latest_command.submit_user)

            elif latest_command.command_type==2:
                self.server_handle.another_lock.acquire()

                another=self.server_handle.another[latest_command.submit_user]

                self.server_handle.another_lock.release()

                self.server_handle.clients_lock.acquire()

                self.server_handle.clients[another].send_message(mp.TCP_Message(4,latest_command.command))

                self.server_handle.clients_lock.release()