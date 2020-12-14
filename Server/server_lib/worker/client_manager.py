import queue
import threading

import server_lib.worker.client_connection as cc
import server_lib.worker.command_pool as cp

import server_lib.server as server

class SubmitForDelete():

    def __init__(self):
        self.id_pool=queue.Queue()
        self.id_pool_lock=threading.Lock()
        self.id_pool_semaphore=threading.Semaphore(0)

    def __del__(self):
        pass

    def submit(self,id:int):
        self.id_pool_lock.acquire()

        self.id_pool.put(id)

        self.id_pool_lock.release()

        self.id_pool_semaphore.release()

    def get(self):
        self.id_pool_semaphore.acquire()

        self.id_pool_lock.acquire()

        latest_id=self.id_pool.get()

        self.id_pool_lock.release()

        return latest_id


class ClientManager(threading.Thread):

    def __init__(self,server_handle):
        super().__init__()

        self.server_handle=server_handle
        self.delete_pool=server_handle.delete_pool

    def __del__(self):
        pass

    def push_shutdown_command(self):
        self.delete_pool.submit(-1)

    def run(self):

        while True:
            id=self.delete_pool.get()

            if id==-1:
                break

            self.server_handle.clients_lock.acquire()

            if id in self.server_handle.clients.keys():
                self.server_handle.another_lock.acquire()

                if id in self.server_handle.another.keys():
                    del self.server_handle.another[id]

                self.server_handle.another_lock.release()

                self.server_handle.clients[id].disconnect()
                self.server_handle.clients[id].wait_for_end()

                del self.server_handle.clients[id]
                self.server_handle.id_pool.return_id(id)

                print('Release ID:',id)

            self.server_handle.clients_lock.release()

        #Clean all clients
        self.server_handle.clients_lock.acquire()

        keys=[i for i in self.server_handle.clients.keys()]

        for id in keys:
            self.server_handle.clients[id].disconnect()
            self.server_handle.clients[id].wait_for_end()

            del self.server_handle.clients[id]
            self.server_handle.id_pool.return_id(id)

        self.server_handle.clients_lock.release()