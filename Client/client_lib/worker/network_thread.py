import threading
import socket

import client_lib.worker.chess_board as chess_board
import client_lib.worker.message_pool as message_pool

class SendThread(threading.Thread):

    def __init__(self,server):
        super().__init__()

        self.father=server

        self.server=server.server

        self.send_pool=message_pool.MessagePool()

    def __del__(self):
        pass

    def send(self,message:message_pool.Message):
        self.send_pool.submit(message)

    def run(self):
        
        while True:
            will_send=self.send_pool.get()

            if will_send.message_type==-1:
                break

            try:
                self.server.sendall(will_send.get_bytes())
            except:
                break


class RecvThread(threading.Thread):

    def __init__(self,server):
        super().__init__()

        self.father=server

        self.server=server.server

        self.player_name=None

    def __del__(self):
        pass

    def run(self):
        
        try:
            while True:

                recv_type=self.server.recv(1)

                if not len(recv_type):
                    raise BaseException()

                recv_type=int.from_bytes(recv_type,byteorder='big',signed=False)

                if recv_type==3:
                    player_order=self.server.recv(1)
                    player_order=int.from_bytes(player_order,byteorder='big',signed=False)

                    self.father.player_order=player_order
                    chess_board.player_order=player_order

                    recv_len=self.server.recv(1)
                    recv_len=int.from_bytes(recv_len,byteorder='big',signed=False)

                    recv_message=self.server.recv(recv_len)
                    self.player_name=recv_message.decode('utf-8')

                    chess_board.another_name=self.player_name

                    print('You matched',self.player_name)

                    if player_order:
                        chess_board.set_waiting(False)
                        print('You play first(White)')
                    else:
                        chess_board.set_waiting(True)
                        print('You play second(Black)')

                    self.father.ready()

                elif recv_type==4:
                    recv_move_x=self.server.recv(2)
                    move_x=int.from_bytes(recv_move_x,byteorder='big',signed=False)

                    recv_move_y=self.server.recv(2)
                    move_y=int.from_bytes(recv_move_y,byteorder='big',signed=False)

                    chess_board.place_chees(1-self.father.player_order,(move_x,move_y))
                    chess_board.set_waiting(False)

                    chess_board.window_name('Your Turn')
        except:
            pass

class ServerConnection():

    def __init__(self,server:socket.socket,show_window:threading.Semaphore):
        super().__init__()

        self.server=server

        self.allow_show=show_window

        self.player_order=None

        self.send_thread=SendThread(self)
        self.recv_thread=RecvThread(self)

    def __del__(self):
        pass

    def send_name(self,name:str):
        self.send_thread.send(message_pool.Message(1,name.encode('utf-8')))

    def ready(self):
        self.allow_show.release()

    def showdown(self):
        self.send_thread.send(message_pool.Message(0,None))

        try:
            self.server.close()
        except:
            pass

        if self.send_thread.isAlive():
            self.send_thread.send(message_pool.Message(-1,None))

    def wait(self):
        if self.send_thread.isAlive():
            self.send_thread.join()

        if self.recv_thread.isAlive():
            self.recv_thread.join()

    def run(self):
        self.send_thread.start()
        self.recv_thread.start()