from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, List, Optional
import numpy as np
import random
import math

### STATE VARS ###
ROW_COUNT = 6
COL_COUNT = 7
AI_PIECE = 1
PLAYER_PIECE = -1
EMPTY = 0
MAX_SPACE = 3
DIFFICULTY_SETTINGS = {
    'easy': {
        'depth': 3,
        'use_strategy': False,
        'check_immediate': False,
        'ai_first': False,
    },
    'medium': {
        'depth': 5,
        'use_strategy': True,
        'check_immediate': True,
        'ai_first': False,
    },
    'hard': {
        'depth': 7,
        'use_strategy': True,
        'check_immediate': True,
        'ai_first': True,
    }
}

### GAME LOGIC ###
# create empty grid with empty string as placaeholders
def create_board():
    return np.zeros((ROW_COUNT, COL_COUNT), dtype='int') 

# returns true if the board has empty spaces
def is_moves_left(board):
    return np.any(board == EMPTY)

# returns true if column has an empty space
def is_valid_location(board, col):
    return board[0][col] == EMPTY

# returns a list of columns with empty spaces
def get_possible_moves(board):
    order = [3, 2, 4, 1, 5, 0, 6]
    return [c for c in order if is_valid_location(board, c)]

# returns a new board with piece placed in the given column
def apply_move(board, col, piece):
    new_board = board.copy()
    for r in range (ROW_COUNT - 1, -1, -1):
        if new_board[r][col] == EMPTY:
            new_board[r][col] = piece
            return new_board
    return new_board
        
# returns true if there are 4 pieces in a row
def detect_win(board, piece):
    # horizontal
    for r in range(ROW_COUNT):
        for c in range(COL_COUNT - 3):
            if board[r][c] == board[r][c+1] == board[r][c+2] == board[r][c+3] == piece:
                return True
    # vertical
    for c in range(COL_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == board[r+1][c] == board[r+2][c] == board[r+3][c] == piece:
                return True
    # diagonal up-right (/)
    for r in range(ROW_COUNT - 3):
        for c in range(COL_COUNT - 3):
            if board[r][c] == board[r+1][c+1] == board[r+2][c+2] == board[r+3][c+3] == piece:
                return True
    # diagonal down-right (\)
    for r in range(3, ROW_COUNT):
        for c in range(COL_COUNT - 3):
            if board[r][c] == board[r-1][c+1] == board[r-2][c+2] == board[r-3][c+3] == piece:
                return True
    return False

# utility funciton (simple)
def evaluate_state_simple(board):
    if detect_win(board, AI_PIECE):
        return 10000
    if detect_win(board, PLAYER_PIECE):
        return -10000
    return 0

# utility function (hard w/ heuristics)
def evaluate_state_hard(board, player):
    score = 0
    # Give more weight to center columns
    for col in range(2, 5):
        for row in range(ROW_COUNT):
            if board[row][col] == player:
                if col == 3:
                    score += 3
                else:
                    score+= 2
    # Horizontal pieces
    for col in range(COL_COUNT - MAX_SPACE):
        for row in range(ROW_COUNT):
            adjacent_pieces = [board[row][col], board[row][col+1], 
                                board[row][col+2], board[row][col+3]] 
            score += evaluate_window(adjacent_pieces, player)
    # Vertical pieces
    for col in range(COL_COUNT):
        for row in range(ROW_COUNT - MAX_SPACE):
            adjacent_pieces = [board[row][col], board[row+1][col], 
                                board[row+2][col], board[row+3][col]] 
            score += evaluate_window(adjacent_pieces, player)
    # Diagonal upwards pieces (/)
    for col in range(COL_COUNT - MAX_SPACE):
        for row in range(ROW_COUNT - MAX_SPACE):
            adjacent_pieces = [board[row][col], board[row+1][col+1], 
                                board[row+2][col+2], board[row+3][col+3]] 
            score += evaluate_window(adjacent_pieces, player)
    # Diagonal downwards pieces (\)
    for col in range(COL_COUNT - MAX_SPACE):
        for row in range(MAX_SPACE, ROW_COUNT):
            adjacent_pieces = [board[row][col], board[row-1][col+1], 
                    board[row-2][col+2], board[row-3][col+3]]
            score += evaluate_window(adjacent_pieces, player)
    return score


# score a window of size 4
def evaluate_window(window, piece):
    window = np.array(window)
    opp = -piece
    num_piece = np.count_nonzero(window == piece)
    num_opp = np.count_nonzero(window == opp)
    num_empty = np.count_nonzero(window == EMPTY)
    score = 0

    # Our threats
    if num_piece == 4:
        # winning
        score += 100000
    elif num_piece == 3 and num_empty == 1:
        # three in a row
        score += 100
    elif num_piece == 2 and num_empty == 2:
        # 2 in a row
        score += 10

    # Opponent threats (slightly stronger to ensure blocking)
    if num_opp == 3 and num_empty == 1:
        score -= 120
    elif num_opp == 2 and num_empty == 2:
        score -= 12

    return score
    
# returns true if in a terminal state
def game_over(board):
    return detect_win(board, AI_PIECE) or detect_win(board, PLAYER_PIECE) or not is_moves_left(board)
      
# returns best move and score using minimax algo
def pick_best_move(board, depth, use_strategy=True, check_immediate=True):
    alpha, beta = -math.inf, math.inf
    best_move, best_value = None, -math.inf

    moves = get_possible_moves(board)
    if not moves:
        return None, -math.inf

    if check_immediate:
        for c in get_possible_moves(board):
            if detect_win(apply_move(board, c, AI_PIECE), AI_PIECE):
                return c, +1_000_000_000
        for c in get_possible_moves(board):
            if detect_win(apply_move(board, c, PLAYER_PIECE), PLAYER_PIECE):
                return c, +999_999  

    for move in moves:
        child = apply_move(board, move, AI_PIECE)
        val = minimax_alpha_beta(child, depth - 1, alpha, beta, False, AI_PIECE, use_strategy)
        if val > best_value:
            best_value, best_move = val, move
        alpha = max(alpha, best_value)
        if alpha >= beta:
            break

    return best_move, best_value

# returns piece that won, or None if draw
def winner(board):
    if detect_win(board, AI_PIECE):
        return AI_PIECE
    if detect_win(board, PLAYER_PIECE):
        return PLAYER_PIECE
    return None

# returns best score using minimax with alpha beta pruning
def minimax_alpha_beta(state, depth, alpha, beta, is_maximizing, player, use_strategy=True):
      if depth == 0 or not is_moves_left(state):
        if use_strategy:
            return evaluate_state_hard(state, player)
        else:
            return evaluate_state_simple(state)
      
      if is_maximizing:
          best_score = -float('inf')
          for move in get_possible_moves(state):
              new_state = apply_move(state, move, AI_PIECE)
              score = minimax_alpha_beta(new_state, depth-1, alpha, beta, False, player, use_strategy)
              best_score = max(score, best_score)
              alpha = max(alpha, best_score)
              if beta <= alpha:
                  break  # Beta cutoff
          return best_score
      else:
          best_score = float('inf')
          for move in get_possible_moves(state):
              new_state = apply_move(state, move, PLAYER_PIECE)
              score = minimax_alpha_beta(new_state, depth-1, alpha, beta, True, player, use_strategy)
              best_score = min(score, best_score)
              beta = min(beta, best_score)
              if beta <= alpha:
                  break  # Alpha cutoff
          return best_score
      
### SCHEMAS ###
Difficulty = Literal["easy", "medium", "hard"]

class NewGameRequest(BaseModel):
    difficulty: Difficulty = "medium"
    aiStarts: bool = False

class MoveRequest(BaseModel):
    board: List[List[int]]
    column: int = Field(ge=0, le=6)
    difficulty: Difficulty = "medium"

class StateResponse(BaseModel):
    board: List[List[int]]
    turn: Literal["player", "ai"]
    over: bool
    winner: Optional[int]          
    aiMove: Optional[int] = None
    legalMoves: List[int]

### ENDPOINTS ###
app = FastAPI()

# initialize game board
@app.post("/games", response_model=StateResponse)
def create_game(req: NewGameRequest):
    board = create_board()
    move = Optional[int] = None # type: ignore

    depth = DIFFICULTY_SETTINGS[req.difficulty]['depth']
    use_strategy = DIFFICULTY_SETTINGS[req.difficulty]['use_strategy']
    check_immediate = DIFFICULTY_SETTINGS[req.difficulty]['check_immediate']

    # make move if ai starts first
    if req.aiStarts:
        c, _ = pick_best_move(board, depth, use_strategy, check_immediate)
        if c is not None:
            board = apply_move(board, c, AI_PIECE)
            move = c

    w = winner(board)
    over = game_over(board)

    return StateResponse(
        board=board.tolist(),
        turn="player",
        over=over,
        winner=w,
        aiMove=move,
        legalMoves=get_possible_moves(board),
    ) 

# update board
@app.post("/update", response_model=StateResponse)
def update_game(req: MoveRequest):
    board = np.array(req.board, dtype="int")
    
    # check player's move
    if not is_valid_location(board, req.column):
        raise HTTPException(status_code=400, detail="Invalid or full column")
    board = apply_move(board, req.column, PLAYER_PIECE)

    w = winner(board)
    if w is not None or not is_moves_left(board):
        return StateResponse(
            board=board.tolist(),
            turn="ai",
            over=True,
            winner=w,
            aiMove=None,
            legalMoves=[],
        )

    depth = DIFFICULTY_SETTINGS[req.difficulty]['depth']
    use_strategy = DIFFICULTY_SETTINGS[req.difficulty]['use_strategy']
    check_immediate = DIFFICULTY_SETTINGS[req.difficulty]['check_immediate']

    move, _ = pick_best_move(board, depth, use_strategy, check_immediate)
    if move is not None:
        board = apply_move(board, move, AI_PIECE)

    w = winner(board)
    over = game_over(board)
    return StateResponse(
        board=board.tolist(),
        turn="player",
        over=over,
        winner=w,
        aiMove=move,
        legalMoves=get_possible_moves(board)
    )
      
### CLI TEST (NOT PART OF API) ###
def main():
    board = create_board()
    Player = 1
    AI = 2
    turn = random.randint(Player, AI)
    
    depth = 5
    while not game_over(board):
        if turn == Player:
            while True:
                col = int(input("Player selected column (0-6): \n"))
                if col < 0 or col > 6:
                    print(f"{col} is invalid. Please pick a number from 0-6")
                    continue
                if is_valid_location(board, col):
                    new_board = apply_move(board, col, PLAYER_PIECE)
                    board = new_board
                    turn = AI
                    break
                else:
                    print(f"Column {col} is full pick another one")
        else:
            move, val = pick_best_move(board, depth + 1)  # not 3
            if move is None:
                break
            board = apply_move(board, move, AI_PIECE) 
            print(f"AI drops in column {move} (eval {val}).")
            print(board)
            turn = Player
    w = winner(board)
    if w == AI_PIECE:
        print("AI wins! Game over.")
    elif w == PLAYER_PIECE:
        print("Player wins! Game over.")
    else:
        print("Draw. Game over.")
                    
if __name__ == "__main__":
    main()
