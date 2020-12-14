import queue
import threading

only_type=[5]
with_len=[3]
without_len=[4]

class TCP_Message():

    def __init__(self,message_type:int,message:bytes):
        self.message_type=message_type
        self.message=message

    def __del__(self):
        pass

    def get_bytes(self):
        message_type=self.message_type.to_bytes(1,byteorder='big',signed=False)

        if self.message_type in only_type:
            return message_type

        message_len=len(self.message)
        message_len=message_len.to_bytes(1,byteorder='big',signed=False)

        if self.message_type in with_len:
            return message_type+message_len+self.message
        elif self.message_type in without_len:
            return message_type+self.message

        return None

class TCP_MessagePool():

    def __init__(self):
        self.pool=queue.Queue()
        self.pool_lock=threading.Lock()
        self.pool_semaphore=threading.Semaphore(0)

    def __del__(self):
        pass

    def send_message(self,message:TCP_Message):
        self.pool_lock.acquire()

        self.pool.put(message)

        self.pool_lock.release()

        self.pool_semaphore.release()

    def get_message(self):
        self.pool_semaphore.acquire()

        self.pool_lock.acquire()

        latest_message=self.pool.get()

        self.pool_lock.release()

        return latest_message
