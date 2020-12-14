import tkinter as tk

import client_lib.worker.message_pool as message_pool
import client_lib.worker.network_thread as network_thread

board_width=720
board_height=720

board=dict()

window=tk.Tk()

cv=tk.Canvas(window,bd=0,background='blue',width=board_width,height=board_height)

back_image=tk.PhotoImage(file='./client_lib/images/Board.png')

network_manager=None

def mouse_click(event):
    click_x=event.x.to_bytes(2,byteorder='big',signed=False)
    click_y=event.y.to_bytes(2,byteorder='big',signed=False)

    will_send=click_x+click_y

    network_manager.send_thread.send(message_pool.Message(2,will_send))

def init_board(server:network_thread.ServerConnection):
    global network_manager
    network_manager=server

    window.resizable(width=False,height=False)

    cv.create_image(362,362,image=back_image)
    cv.pack()

def window_name(name:str):
    window.title(name)

def bind_event():
    cv.bind('<Button-1>',mouse_click)

def place_chees():
    board.clear()

def clear_board():
    board.clear()

def main_loop():
    window.mainloop()
