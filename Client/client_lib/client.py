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

        chess_board.network_manager=self.network

        chess_board.init_board()
        chess_board.bind_event()

    def __del__(self):
        pass

    def run(self):
        print('Input your name:',end='')
        self.name=input()

        chess_board.my_name=self.name

        print('Connecting to server')
        self.server.connect((self.ip,self.port))
        print('Connected to server')

        print('Waiting for another player')

        self.network.run()

        self.network.send_name(self.name)

        self.show_window.acquire()

        chess_board.clear_board()

        if chess_board.player_order:
            chess_board.window_name('Your Turn')
        else:
            chess_board.window_name('Waiting for Another')

        chess_board.main_loop()

        print('Game done & Bye~')

        self.network.showdown()
        self.network.wait()

