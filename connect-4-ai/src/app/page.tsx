"use client";
import "@/app/home_page.css"
import { useRouter } from "next/navigation";
import { useState} from "react";
export default function Home() {
  const router = useRouter();
  const [colorEasy, setColorEasy] = useState<string>("#32a852");
  const [colorMed, setColorMed] = useState<string>("#f0ed43");
  const [colorHard, setColorHard] = useState<string>("#bf1b1b");
  const toggleColorEasy = (color: string, setColor: (color: string) => void) => {
    setColor(color === "#32a852" ? "#216333" : "#32a852");
  };
  const toggleColorMed = (color: string, setColor: (color: string) => void) => {
    setColor(color === "#f0ed43" ? "#aba92e" : "#f0ed43");
  };
  const toggleColorHard = (color: string, setColor: (color: string) => void) => {
    setColor(color === "#bf1b1b" ? "#6b1010" : "#bf1b1b");
  };
  
  function startGame(difficulty: "easy" | "medium" | "hard") {
    router.push(`/connect_four_page?difficulty=${difficulty}`);
  }
  return (
    
    <div>
      <div className = "content">
      <div className="title"> Welcome to Connect 4</div>
      <div className="center">Pick a Level</div>
      <button 
        type = "button"
        onClick={() => { toggleColorEasy(colorEasy, setColorEasy); startGame("easy"); }}
        className="easy_btn"
        style={{ backgroundColor: colorEasy }}>
        Easy
      </button>
      <button 
      type = "submit"
      onClick={() => { toggleColorMed(colorMed, setColorMed); startGame("medium"); }}
      className="med_btn"
      style={{ backgroundColor: colorMed }}>
      Medium
      </button>
      <button 
      type = "submit"
      onClick={() => { toggleColorHard(colorHard, setColorHard); startGame("hard"); }}
      className="hard_btn"
      style={{backgroundColor: colorHard }}>
      Hard
      </button>
      </div>
    </div>
    
  );
}
