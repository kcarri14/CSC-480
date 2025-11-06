export type Difficulty = "easy" | "medium" | "hard";

export type Game = {
    board: number[][];
    turn: "player" | "ai";
    over: boolean;
    winner: 1 | -1 | null;
    aiMove?: number | null;
    legalMoves: number[];
};

const BASE = "http://127.0.0.1:8000";

export async function newGame(difficulty: Difficulty) {
  const aiStarts = difficulty === "hard";
  const res = await fetch(`${BASE}/new-game`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ difficulty, aiStarts }),
  });
  if (!res.ok) throw new Error(await res.text());
  return (await res.json()) as Game;
}

export async function makeMove(board: number[][], column: number, difficulty: Difficulty) {
  const res = await fetch(`${BASE}/move`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ board, column, difficulty }),
  });
  if (!res.ok) throw new Error(await res.text());
  return (await res.json()) as Game;
}