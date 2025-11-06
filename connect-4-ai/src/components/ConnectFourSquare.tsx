// src/components/ConnectFourSquare.tsx
"use client";
import "@/app/connect_four_page/connect_four.css";

export default function ConnectFourSquare({
  value,
  onClick,
  disabled,
}: {
  value: number; 
  onClick: () => void;
  disabled: boolean;
}) {
  let className = "cell";
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
