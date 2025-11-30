"use client";
import "@/app/connect_four_page/connect_four.css";

export default function ConnectFourSquare({
  value,
  onClick,
  disabled,
  isWinning,
}: {
  value: number; 
  onClick: () => void;
  disabled: boolean;
  isWinning?: boolean;
}) {
  let className = "cell";
  if (isWinning) className = "cell-winning";
  if (value === 1) className += " ai";
  else if (value === -1) className += " player";
  return (
    <button
      className={className}
      onClick={onClick}
      disabled={disabled}
    />
  );
}
