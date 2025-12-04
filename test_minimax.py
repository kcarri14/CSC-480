import random
import numpy as np
import pytest
from main import (
    create_board,
    apply_move,
    get_possible_moves,
    pick_best_move,
    game_over,
    winner,
    detect_win,
)

# unit tests
def test_apply_move():
    board = create_board()
    board = apply_move(board, 3, 1)
    assert board[5][3] == 1

def test_column_stacking():
    board = create_board()
    board = apply_move(board, 0, 1)
    board = apply_move(board, 0, -1)
    assert board[5][0] == 1
    assert board[4][0] == -1

def test_get_possible_moves():
    board = create_board()
    for i in range(6):
        board = apply_move(board, 0, 1)
    possible_moves = get_possible_moves(board)
    assert 0 not in possible_moves
    assert len(possible_moves) == 6

def test_horizontal_win():
    board = create_board()
    for i in range(4):
        board = apply_move(board, i, 1)

    win, pieces = detect_win(board, 1)
    assert win is True
    assert pieces == [(5,0), (5,1), (5,2), (5,3)]

def test_vertical_win():
    board = create_board()
    for i in range(4):
        board = apply_move(board, 6, 1)
    
    win, pieces = detect_win(board, 1)
    assert win is True
    assert pieces == [(2,6), (3,6), (4,6), (5,6)]

def test_diagonal_win():
    board = create_board()
    board = apply_move(board, 1, 1)
    board = apply_move(board, 2, 1)
    board = apply_move(board, 2, 1)
    board = apply_move(board, 3, 1)
    board = apply_move(board, 3, 1)
    board = apply_move(board, 3, 1)

    board = apply_move(board, 0, -1)
    board = apply_move(board, 1, -1)
    board = apply_move(board, 2, -1)
    board = apply_move(board, 3, -1)

    win, pieces = detect_win(board, -1)
    assert win is True
    assert len(pieces) == 4

def test_pick_best_move_easy():
    board = create_board()
    for i in [0,1,2]:
        board = apply_move(board, i, 1)
    
    move, score = pick_best_move(board, depth=3, max_piece=1, use_strategy=False, check_immediate=False)
    assert move == 3

def test_block_win_easy():
    board = create_board()
    for i in [0,1,2]:
        board = apply_move(board, i, -1)
    
    move, score = pick_best_move(board, depth=3, max_piece=1, use_strategy=False, check_immediate=False)
    assert move == 3

# game simulations
# randomly chooses a valid column to play
def get_random_move(board):
    possible_moves = get_possible_moves(board)
    return random.randint(0, len(possible_moves)-1)

# simulates a single connect 4 game
def simulate_random_game(depth_ai, use_strategy_ai=True, check_immediate_ai=True):
    board = create_board()
    turn = "opp"

    while not game_over(board):
        if turn == "ai":
            move, _ = pick_best_move(board, depth_ai, 1, use_strategy_ai, check_immediate_ai)
            if move is None:
                break
            board = apply_move(board, move, 1)
            turn = "opp"
        else:
            move = get_random_move(board)
            if move is None:
                break
            board = apply_move(board, move, -1)
            turn = "ai"

    win, _ = winner(board)

    if win == 1:
        return "ai"
    elif win == -1:
        return "opp"
    return "draw"

# simulates multiple games
def simulate_matches(num_games=1000, depth_ai=3, use_strategy_ai=False, check_immediate_ai=False): 
    print("Num games:", num_games)
    print("Depth AI", depth_ai)
    print("Use strategy AI", use_strategy_ai)
    print("Check immediate AI", check_immediate_ai)
    num_ai = 0
    num_opp = 0
    num_draw = 0

    for i in range(num_games):
        print("game", i)
        outcome= simulate_random_game(depth_ai, use_strategy_ai, check_immediate_ai)
        if outcome == "ai":
            num_ai += 1
        elif outcome == "opp":
            num_opp += 1
        else:
            num_draw += 1

    print("AI won", num_ai, "lost", num_opp, "games and drew", num_draw, "games")

if __name__ == "__main__":
    simulate_matches()

    # random against easy AI parameters: AI won 945 lost 55 games and drew 0 games
    # random against medium AI parameters: AI won 995 lost 5 games and drew 0 games