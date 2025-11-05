export type Difficulty = "easy" | "medium" | "hard";

export type Game = {
    board: number[][];
    turn: "player" | "ai";
    over: boolean;
    winner: 1 | -1 | null;
    aiMove?: number | null;
    legalMoves: number[];
};

const BASE = "http://localhost:8000";

export async function newGame(
    difficulty: Difficulty = "medium",
    aiStarts: boolean = false
): Promise<Game> {
    const res = await fetch(`{BASE}/new_game`, {
        method: "POST",
        headers: {"Content=Type": "application/json"},
        body: JSON.stringify({ difficulty, aiStarts })
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
}

export async function makeMove(
    board: number[][],
    column: number,
    difficulty: Difficulty = "medium"
): Promise<Game> {
        const res = await fetch(`{BASE}/move`, {
        method: "POST",
        headers: {"Content=Type": "application/json"},
        body: JSON.stringify({ board, column, difficulty })
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
}