#game: connect 4
import numpy as np
import random

row_count = 6
col_count = 7

def create_board():
    return np.full((row_count, col_count), '', dtype='<U1') 

def is_moves_left(board):
    return np.any(board == '')

def is_valid_location(board, col):
    return board[0][col] == ''

def get_possible_moves(board):
    order = [3, 2, 4, 1, 5, 0, 6]
    return [c for c in order if is_valid_location(board, c)]

def evaluate_state(b):
    #vertical win
    for row in range(row_count):
        for col in range(col_count - 3):
            if b[row][col] == b[row][col+1] == b[row][col+ 2] == b[row][col+3] == 'o':
                return 10
            if b[row][col] == b[row][col+1] == b[row][col+ 2] == b[row][col+3] == 'x':
                return -10
    #horizontal win
    for col in range(col_count):
        for row in range(row_count -3):
            if b[row][col] == b[row+1][col] == b[row+2][col] == b[row+3][col] == 'o':   
                return 10
            if b[row][col] == b[row+1][col] == b[row+2][col] == b[row+3][col] == 'x':   
                return -10
    #diagonal win upwards
    for row in range(row_count-3):
        for col in range(col_count -3):
            if b[row][col] == b[row+1][col+1] == b[row+2][col+ 2] == b[row+3][col+3] == 'o':            
                return 10
            if b[row][col] == b[row+1][col+1] == b[row+2][col+ 2] == b[row+3][col+3] == 'x':            
                return -10
    #diagonal win downwards
    for row in range(3, row_count):
        for col in range(col_count -3):
            if b[row][col] == b[row-1][col+1] == b[row-2][col+ 2] == b[row-3][col+3] == 'o':            
                return 10
            if b[row][col] == b[row-1][col+1] == b[row-2][col+ 2] == b[row-3][col+3] == 'x':            
                return -10
    return 0


def apply_move(board, col, piece):
    new_state = board.copy()
    #print(new_state)
    for r in range(row_count -1, -1, -1):
        #print(r)
        if new_state[r][col] == '':
            new_state[r][col] = piece
            #print(new_state)
            return new_state
            
def minimax(state, depth, is_maximizing):
      if depth == 0 or game_over_(state):
          return evaluate_state(state)
      
      if is_maximizing:
          best_score = -float('inf')
          for move in get_possible_moves(state):
              new_state = apply_move(state, move)
              score = minimax(new_state, depth-1, False)
              best_score = max(score, best_score)
          return best_score
      else:
          best_score = float('inf')
          for move in get_possible_moves(state):
              new_state = apply_move(state, move)
              score = minimax(new_state, depth-1, True)
              best_score = min(score, best_score)
          return best_score

def pick_best_move(board, depth, ai_piece):
    #print("inside pick best move")
    curr = ai_piece
    #print("found current player")
    #print(curr)
    ai_turn = (ai_piece == curr)
    #print(ai_turn)
    want_max = (ai_piece == 'o' and ai_turn) or (ai_piece == 'x' and not ai_turn)
    #print(want_max)
    best_move = None
    best_value = -float('inf') if want_max else float('inf')
    #print(best_value)
    for move in get_possible_moves(board):
        #print("inside get possible moves")
        child = apply_move(board, move, ai_piece)
        #print(child)
        score = minimax(child, depth-1, not want_max)
        #print(score)
        if want_max:
            if score > best_value:                
                best_value, best_move = score, move
        else:
            if score < best_value:               
                best_value, best_move = score, move
    return best_move, best_value

def game_over(x):
    if x == 1:
        return False
    else:
        return True
    
def game_over_(board):
    return evaluate_state(board) == 0 or not is_moves_left(board)

def winner(board):
    score = evaluate_state(board)
    if score == 10:  return 'o'
    if score == -10: return 'x'
    return None
      

def main():
    Player = 1
    AI = 2
    board = create_board()
    turn = random.randint(Player, AI)
    ai_piece = 'o'
    player_piece = 'x'
    #print(board)
    depth = 10
    while game_over_(board):
        if turn == Player:
            while True:
                col = int(input("Player selected column (0-6): \n"))
                if is_valid_location(board, col):
                    new_board = apply_move(board, col, player_piece)
                    board = new_board
                    turn = AI
                    break
                else:
                    print("Column {col} is full pick another one")
        else:
            #print("inside the else in main")
            move, val = pick_best_move(board, depth + 1, ai_piece)  # not 3
            if move is None:
                #print("No legal moves. Draw.")
                break
            board = apply_move(board, move, ai_piece) 
            print(f"AI drops in column {move} (eval {val}).")
            print(board)
            turn = Player
    w = winner(board)
    if w == 'o':
        print("AI wins! Game over.")
    elif w == 'x':
        print("Player wins! Game over.")
    else:
        print("Draw. Game over.")

                    

if __name__ == "__main__":
    main()


        