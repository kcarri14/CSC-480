import numpy as np
import random
import math

row_count = 6
col_count = 7
Player = 1
AI = 2
ai_piece = 'o'
player_piece = 'x'
max_space = 3

# create empty grid with empty string as placaeholders
def create_board():
    return np.full((row_count, col_count), '', dtype='<U1') 

# returns true if the board has empty spaces
def is_moves_left(board):
    return np.any(board == '')

# returns true if column has an empty space
def is_valid_location(board, col):
    return board[0][col] == ''

# returns a list of columns with empty spaces
def get_possible_moves(board):
    order = [3, 2, 4, 1, 5, 0, 6]
    return [c for c in order if is_valid_location(board, c)]

# returns a new board with piece placed in the given column
def apply_move(board, col, piece):
    new_state = board.copy()
    for r in range (row_count -1, -1, -1):
        if new_state[r][col] == '':
            new_state[r][col] = piece
            return new_state
        
# returns true if there are 4 pieces in a row
def detect_win(board, piece):
    # horizontal
    for r in range(row_count):
        for c in range(col_count - 3):
            if board[r][c] == board[r][c+1] == board[r][c+2] == board[r][c+3] == piece:
                return True
    # vertical
    for c in range(col_count):
        for r in range(row_count - 3):
            if board[r][c] == board[r+1][c] == board[r+2][c] == board[r+3][c] == piece:
                return True
    # diagonal up-right (/)
    for r in range(row_count - 3):
        for c in range(col_count - 3):
            if board[r][c] == board[r+1][c+1] == board[r+2][c+2] == board[r+3][c+3] == piece:
                return True
    # diagonal down-right (\)
    for r in range(3, row_count):
        for c in range(col_count - 3):
            if board[r][c] == board[r-1][c+1] == board[r-2][c+2] == board[r-3][c+3] == piece:
                return True
    return False

# utility funciton (simple)
def evaluate_state_simple(board):
    if detect_win(board, ai_piece):
        return 10000
    if detect_win(board, player_piece):
        return -10000
    return 0

# utility function (hard)
def evaluate_state_hard(board, player):
    score = 0
    # Give more weight to center columns
    for col in range(2, 5):
        for row in range(row_count):
            if board[row][col] == player:
                if col == 3:
                    score += 3
                else:
                    score+= 2
    # Horizontal pieces
    for col in range(col_count - max_space):
        for row in range(row_count):
            adjacent_pieces = [board[row][col], board[row][col+1], 
                                board[row][col+2], board[row][col+3]] 
            score += evaluate_window(adjacent_pieces, player)
    # Vertical pieces
    for col in range(col_count):
        for row in range(row_count - max_space):
            adjacent_pieces = [board[row][col], board[row+1][col], 
                                board[row+2][col], board[row+3][col]] 
            score += evaluate_window(adjacent_pieces, player)
    # Diagonal upwards pieces
    for col in range(col_count - max_space):
        for row in range(row_count - max_space):
            adjacent_pieces = [board[row][col], board[row+1][col+1], 
                                board[row+2][col+2], board[row+3][col+3]] 
            score += evaluate_window(adjacent_pieces, player)
    # Diagonal downwards pieces
    for col in range(col_count - max_space):
        for row in range(max_space, row_count):
            adjacent_pieces = [board[row][col], board[row-1][col+1], 
                    board[row-2][col+2], board[row-3][col+3]]
            score += evaluate_window(adjacent_pieces, player)
    return score


# score a window of size 4
def evaluate_window(window, piece):
    opp = player_piece if piece == ai_piece else ai_piece
    cnt_p = window.count(piece) # our piece
    cnt_o = window.count(opp) # opposing piece
    cnt_e = window.count('') # empty piece
    score = 0

    # Our threats
    if cnt_p == 4:
        # winning
        score += 100000
    elif cnt_p == 3 and cnt_e == 1:
        # three in a row
        score += 100
    elif cnt_p == 2 and cnt_e == 2:
        # 2 in a row
        score += 10

    # Opponent threats (slightly stronger to ensure blocking)
    if cnt_o == 3 and cnt_e == 1:
        score -= 120
    elif cnt_o == 2 and cnt_e == 2:
        score -= 12

    return score
    
# returns true if in a terminal state
def game_over(board):
    return detect_win(board, ai_piece) or detect_win(board, player_piece) or not is_moves_left(board)
      
# returns best move and score using minimax algo
def pick_best_move(board, depth, ai_piece=ai_piece):
    maximizing_for_ai = True  
    alpha, beta = -math.inf, math.inf
    best_move, best_value = None, -math.inf

    
    for c in get_possible_moves(board):
        if detect_win(apply_move(board, c, ai_piece), ai_piece):
            return c, +1_000_000_000
    for c in get_possible_moves(board):
        if detect_win(apply_move(board, c, player_piece), player_piece):
            return c, +999_999  

    for move in get_possible_moves(board):
        child = apply_move(board, move, ai_piece)
        val = minimax_alpha_beta(child, depth - 1, alpha, beta, not maximizing_for_ai, ai_piece, False)
        if val > best_value:
            best_value, best_move = val, move
        alpha = max(alpha, best_value)
        if alpha >= beta:
            break

    return best_move, best_value

# returns piece that won, or None if draw
def winner(board):
    if detect_win(board, ai_piece):
        return ai_piece
    if detect_win(board, player_piece):
        return player_piece
    return None

# returns best score using minimax with alpha beta pruning
def minimax_alpha_beta(state, depth, alpha, beta, is_maximizing, player, easy=True):
      print('easy mode on: ', easy)
      if depth == 0 or is_moves_left(state):
        if easy:
            return evaluate_state_simple(state)
        else:
            return evaluate_state_hard(state, player)
      
      if is_maximizing:
          best_score = -float('inf')
          for move in get_possible_moves(state):
              new_state = apply_move(state, move)
              score = minimax_alpha_beta(new_state, depth-1, alpha, beta, False)
              best_score = max(score, best_score)
              alpha = max(alpha, best_score)
              if beta <= alpha:
                  break  # Beta cutoff
          return best_score
      else:
          best_score = float('inf')
          for move in get_possible_moves(state):
              new_state = apply_move(state, move)
              score = minimax_alpha_beta(new_state, depth-1, alpha, beta, True)
              best_score = min(score, best_score)
              beta = min(beta, best_score)
              if beta <= alpha:
                  break  # Alpha cutoff
          return best_score
      
def main():
    board = create_board()
    turn = random.randint(Player, AI)
    
    #print(board)
    depth = 10 
    while not game_over(board):
        if turn == Player:
            while True:
                col = int(input("Player selected column (0-6): \n"))
                if col < 0 or col > 6:
                    print(f"{col} is invalid. Please pick a number from 0-6")
                    break
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
    print(board)
    if w == 'o':
        print("AI wins! Game over.")
    elif w == 'x':
        print("Player wins! Game over.")
    else:
        print("Draw. Game over.")
                    
if __name__ == "__main__":
    main()
