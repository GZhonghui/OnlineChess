import tkinter as tk
import threading
import math

import client_lib.worker.message_pool as message_pool
import client_lib.worker.network_thread as network_thread

board_width=720
board_height=720

board_size=19

board_range=(24,698)

board=dict()
board_lock=threading.Lock()

window=tk.Tk()

cv=tk.Canvas(window,bd=0,background='blue',width=board_width,height=board_height)

back_image=tk.PhotoImage(file='./client_lib/images/Board.png')

network_manager=None

def distance(point_x:tuple,point_y:tuple):
    dx=point_x[0]-point_y[0]
    dy=point_x[1]-point_y[1]

    return math.sqrt(dx*dx+dy*dy)

def convert_to_point(x:int):
    block=(board_range[1]-board_range[0]+1)/(board_size-1)
    return math.floor((x-board_range[0])/block)

def convert_to_pos(x:int):
    block=(board_range[1]-board_range[0]+1)/(board_size-1)
    return board_range[0]+x*block

def point_availeable(pos:tuple):
    if pos[0]<0 or pos[0]>=board_size:
        return False

    if pos[1]<0 or pos[1]>=board_size:
        return False

    return True

def convert_click_to_pos(click_pos:tuple):
    chess_x=convert_to_point(click_pos[0])
    chess_y=convert_to_point(click_pos[1])

    res_pos=None
    res_dis=8.0

    for x_offset in range(2):
        for y_offset in range(2):
            this_point=(chess_x+x_offset,chess_y+y_offset)

            if point_availeable(this_point):
                point_pos=(convert_to_pos(this_point[0]),convert_to_pos(this_point[1]))
                if distance(point_pos,click_pos)<res_dis:
                    res_dis=distance(point_pos,click_pos)
                    res_pos=this_point
    return res_pos

def mouse_click(event):
    click_point=convert_click_to_pos((event.x,event.y))

    if click_point is None:
        return

    place_chees(1,click_point)

    (click_x,click_y)=click_point

    click_x=click_x.to_bytes(2,byteorder='big',signed=False)
    click_y=click_y.to_bytes(2,byteorder='big',signed=False)

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

def get_chess(pos:tuple):
    if pos in board.keys():
        return board[pos]
    return None

def place_chees(chess:int,pos:tuple):
    board_lock.acquire()

    board[pos]=chess

    p=(convert_to_pos(pos[0]),convert_to_pos(pos[1]))

    r=17

    cv.create_oval(p[0]-r,p[1]-r,p[0]+r,p[1]+r,fill='white' if chess else 'black')

    board_lock.release()

def clear_board():
    board.clear()

def main_loop():
    window.mainloop()
