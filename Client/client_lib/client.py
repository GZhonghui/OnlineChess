import socket
import threading

import client_lib.worker.chess_board as chess_board
import client_lib.worker.network_thread as network_thread

class ClientHandle():

    def __init__(self,ip:str,port=12346):
        self.ip=ip
        self.port=port

        self.server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        self.show_window=threading.Semaphore(0)

        self.network=network_thread.ServerConnection(self.server,self.show_window)

        chess_board.init_board(self.network)
        chess_board.bind_event()

    def __del__(self):
        pass

    def run(self):
        print('Input your name:',end='')
        self.name=input()

        chess_board.window_name(self.name)

        print('Connecting to server')
        self.server.connect((self.ip,self.port))
        print('Connected to server')

        self.network.run()

        self.network.send_name(self.name)

        print('Waiting for another player')

        self.show_window.acquire()

        print('Found player:',self.network.recv_thread.player_name)

        chess_board.clear_board()

        chess_board.main_loop()

        print('Game done & Bye~')

        self.network.showdown()
        self.network.wait()

