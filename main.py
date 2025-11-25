from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal, List, Optional, Tuple
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
        'depth': 6,
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
        
# returns true if there are 4 pieces in a row along with a list of coordinates, false and empty list otherwise
def detect_win(board, piece):
    # horizontal
    for r in range(ROW_COUNT):
        for c in range(COL_COUNT - 3):
            if board[r][c] == board[r][c+1] == board[r][c+2] == board[r][c+3] == piece:
                winning_pieces = [(r,c), (r, c+1), (r, c+2), (r, c+3)]
                return True, winning_pieces
    # vertical
    for c in range(COL_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == board[r+1][c] == board[r+2][c] == board[r+3][c] == piece:
                winning_pieces = [(r,c), (r+1, c), (r+2, c), (r+3, c)]
                return True, winning_pieces
    # diagonal up-right (/)
    for r in range(ROW_COUNT - 3):
        for c in range(COL_COUNT - 3):
            if board[r][c] == board[r+1][c+1] == board[r+2][c+2] == board[r+3][c+3] == piece:
                winning_pieces = [(r,c), (r+1, c+1), (r+2, c+2), (r+3, c+3)]
                return True, winning_pieces
    # diagonal down-right (\)
    for r in range(3, ROW_COUNT):
        for c in range(COL_COUNT - 3):
            if board[r][c] == board[r-1][c+1] == board[r-2][c+2] == board[r-3][c+3] == piece:
                winning_pieces = [(r,c), (r-1, c+1), (r-2, c+2), (r-3, c+3)]
                return True, winning_pieces
    return False, []

# utility funciton (simple)
def evaluate_state_simple(board):
    status, _ = detect_win(board, AI_PIECE)
    if status:
        return 10000
    status, _ = detect_win(board, PLAYER_PIECE)
    if status:
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
    ai_won, _ = detect_win(board, AI_PIECE)
    player_won, _ = detect_win(board, PLAYER_PIECE)
    return ai_won or player_won or not is_moves_left(board)
      
# returns best move and score using minimax algo
def pick_best_move(board, depth, use_strategy=True, check_immediate=True):
    alpha, beta = -math.inf, math.inf
    best_move, best_value = None, -math.inf

    moves = get_possible_moves(board)
    if not moves:
        return None, -math.inf

    if check_immediate:
        for c in get_possible_moves(board):
            status = detect_win(apply_move(board, c, AI_PIECE), AI_PIECE)
            if status:
                return c, +1_000_000_000
        for c in get_possible_moves(board):
            status = detect_win(apply_move(board, c, PLAYER_PIECE), PLAYER_PIECE)
            if status:
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

# returns piece that won and list of coordinates, or None if draw
def winner(board):
    status, winning_pieces = detect_win(board, AI_PIECE)
    if status:
        return AI_PIECE, winning_pieces
    status, winning_pieces = detect_win(board, PLAYER_PIECE)
    if status:
        return PLAYER_PIECE, winning_pieces
    return None, []

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
    winning_pieces: List[Tuple[int, int]]
    aiMove: Optional[int] = None
    legalMoves: List[int]

### ENDPOINTS ###
app = FastAPI()

# CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# initialize game board
@app.post("/new-game", response_model=StateResponse)
def create_game(req: NewGameRequest):
    board = create_board()
    move: Optional[int] = None # type: ignore

    depth = DIFFICULTY_SETTINGS[req.difficulty]['depth']
    use_strategy = DIFFICULTY_SETTINGS[req.difficulty]['use_strategy']
    check_immediate = DIFFICULTY_SETTINGS[req.difficulty]['check_immediate']

    # make move if ai starts first
    if req.aiStarts:
        c, _ = pick_best_move(board, depth, use_strategy, check_immediate)
        if c is not None:
            board = apply_move(board, c, AI_PIECE)
            move = c

    w, pieces = winner(board)
    over = game_over(board)

    print(board)

    return StateResponse(
        board=board.tolist(),
        turn="player",
        over=over,
        winner=w,
        winning_pieces=pieces,
        aiMove=move,
        legalMoves=get_possible_moves(board),
    ) 

# update board
@app.post("/move", response_model=StateResponse)
def update_game(req: MoveRequest):
    board = np.array(req.board, dtype="int")
    
    # check player's move
    if not is_valid_location(board, req.column):
        raise HTTPException(status_code=400, detail="Invalid or full column")
    board = apply_move(board, req.column, PLAYER_PIECE)

    w, pieces = winner(board)
    if w:
        print(pieces)
    if w is not None or not is_moves_left(board):
        return StateResponse(
            board=board.tolist(),
            turn="ai",
            over=True,
            winner=w,
            winning_pieces=pieces,
            aiMove=None,
            legalMoves=[],
        )

    depth = DIFFICULTY_SETTINGS[req.difficulty]['depth']
    use_strategy = DIFFICULTY_SETTINGS[req.difficulty]['use_strategy']
    check_immediate = DIFFICULTY_SETTINGS[req.difficulty]['check_immediate']

    move, _ = pick_best_move(board, depth, use_strategy, check_immediate)
    if move is not None:
        board = apply_move(board, move, AI_PIECE)

    w, pieces = winner(board)
    if w:
        print(pieces)
    over = game_over(board)
    return StateResponse(
        board=board.tolist(),
        turn="player",
        over=over,
        winner=w,
        winning_pieces=pieces,
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
