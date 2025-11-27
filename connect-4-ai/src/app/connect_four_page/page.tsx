"use client";

import "@/app/connect_four_page/connect_four.css";
import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import type { Difficulty, Game } from "@/lib/api";
import { newGame, makeMove } from "@/lib/api";
import ConnectFourSquare from "@/components/ConnectFourSquare";
import Link from "next/link";


const ROWS = 6;
const COLS = 7;

function getStatusText(s: Game): string {
  if (s.over) {
    if (s.winner === 1) return "AI wins!";
    if (s.winner === -1) return "You win!";
    return "Draw!";
  }
  return "Play!";
}

const handleReload = () => {
  window.location.reload();
}



export default function ConnectFourPage() {
  // get difficulty level from url
  const params = useSearchParams();
  const difficulty = (params.get("difficulty") ?? "medium") as Difficulty;

  // get board state
  const [board, setBoard] = useState<number[][]>(
    Array.from({ length: ROWS }, () => Array.from({ length: COLS }, () => 0))
  );
  const [game, setGame] = useState<Game | null>(null);
  const [loading, setLoading] = useState(false);

  // disable clicking for columns
  const canClick = useMemo(
    () => !!game && !game.over && game.turn === "player" && !loading,
    [game, loading]
  );

  // highlight winning pieces
  const winningPieces = useMemo(() => {
    if (!game || !game.winning_pieces?.length) return new Set<string>();
    return new Set(
      game.winning_pieces.map(([r, c]) => `${r}-${c}`)
    );
  }, [game?.winning_pieces]);


  // Create a new game on mount / difficulty change
  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const g = await newGame(difficulty);
        setGame(g);
        setBoard(g.board);
      } finally {
        setLoading(false);
      }
    })();
  }, [difficulty]);

  async function handleTurn(col: number) {
    if (!game || !canClick) return;
    setLoading(true);
    try {
      const next = await makeMove(board, col, difficulty);
      setGame(next);
      setBoard(next.board);
    } catch (e) {
      console.error(e);
      alert(String(e));
    } finally {
      setLoading(false);
    }
  }

  if (!game) return <div className="loading">Loading…</div>;

  return (
    <div>
      <h1 className="game-title">Connect 4</h1>
      <p className="game-level">Game Difficulty: {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}</p>
      <p className="game-status">{getStatusText(game)}</p>
      <div className="board">
        {board.map((row, rIdx) =>
          row.map((value, cIdx) => {
            const isWinning = winningPieces.has(`${rIdx}-${cIdx}`);
            return (
              <ConnectFourSquare
                key={`${rIdx}-${cIdx}`}
                value={value} // 0 / -1 / 1
                onClick={() => handleTurn(cIdx)}
                disabled={!canClick || !game.legalMoves.includes(cIdx)}
                isWinning={isWinning}
              />
            );
          })
        )}
      </div>
      <div className="centered">
      <button type="button" onClick={handleReload} className="button">
        Restart Game
      </button>
      </div>
      <div className="centered">
      <Link href={"/home_page"}>Back to Home</Link>
      </div>
    </div>
  );
}
