import random
import numpy as np
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from main import (
    create_board,
    apply_move,
    get_possible_moves,
    pick_best_move,
    game_over,
    winner,
    detect_win,
    app,
)

client = TestClient(app)

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
    
    move, _ = pick_best_move(board, depth=3, max_piece=1, use_strategy=False, check_immediate=False)
    assert move == 3

def test_game_over():
    board = create_board()
    for r in range(6):
        for c in range(7):
            piece = 1 if r % 2 == 0 else -1
            board = apply_move(board, c, piece)
    
    over = game_over(board)
    assert over == True

    moves = get_possible_moves(board)
    assert len(moves) == 0


def test_full_board():
    board = create_board()
    for c in range(7):
        if c == 3:
            continue # skip col 3
        for r in range(6):
            piece = 1 if r % 2 == 0 else -1
            board = apply_move(board, c, piece)

    possible = get_possible_moves(board)
    assert possible == [3]

def test_win_over_block():
    board = create_board()
    for r in range(3):
        board = apply_move(board, 0, 1)
        board = apply_move(board, 1, -1)

    move, _ = pick_best_move(board, depth=5, max_piece = 1, use_strategy=True, check_immediate=True)
    assert move == 0

    board = apply_move(board, move, 1)
    win, _ = detect_win(board, 1)
    assert win is True

# client tests
def test_invalid_move_small():
    board = create_board().tolist()

    req = {
        "board": board,
        "column": -1,
        "difficulty": "medium",
    }

    resp = client.post("/update-board", json=req)
    assert resp.status_code == 422

def test_raise_exception():
    board = create_board()
    for i in range(6):
        board = apply_move(board, 0, 1)
    board = board.tolist()
    req = {
        "board": board,
        "column": 0,
        "difficulty": "easy",
    }

    resp = client.post("/update-board", json=req)
    assert resp.status_code == 400


def test_invalid_move_large():
    board = create_board().tolist()

    req = {
        "board": board,
        "column": 7,
        "difficulty": "medium",
    }

    resp = client.post("/update-board", json=req)
    assert resp.status_code == 422

def test_invalid_board():
    board = [[0,0,0,0,0,0],
             [0,0,0,0,0,0],
             [0,0,0,0,0,0],
             [0,0,0,0,0,0],
             [0,0,0,0,0,0],
             [0,0,0,0,0,0],
             [0,0,0,0,0,0]]
    req = {
        "board": board,
        "difficulty": "medium"
    }

    resp = client.post("/make-move", json=req)
    assert resp.status_code == 400

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