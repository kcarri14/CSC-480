
import numpy as np
import math
import random

rows = 6
columns = 7
player = 0
agent = 1

player_piece = 1
agent_piece = 2



def board():
    return np.zeros((rows, columns))

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[rows -1][col] == 0

def get_next_open_row(board, col):
    for i in range(rows):
        if board[i][col] == 0:
            return i
        
def get_valid_location(board):
    valid_locations = []
    for column in range(columns):
        if is_valid_location(board, column):
            valid_locations.append(column)
    return valid_locations        

def print_board(board):
    return

def winning_move(board, piece):
    return










