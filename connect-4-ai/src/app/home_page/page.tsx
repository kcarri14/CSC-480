"use client";
import "@/app/home_page/home_page.css"
import Link from 'next/link';
import { useState} from "react";
export default function Home() {
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
  return (
    
    <div>
      <div className = "content">
      <div className="title"> Welcome to Connect 4</div>
      <div className="center">Pick a Level</div>
      <button type = "submit"
            onClick={() => toggleColorEasy(colorEasy, setColorEasy)}
            className="easy_btn"
            style={{
              backgroundColor: colorEasy,
            }}><Link href="/connect_four_page">Easy</Link></button>
      <button type = "submit"
            onClick={() => toggleColorMed(colorMed, setColorMed)}
            className="med_btn"
            style={{
              backgroundColor: colorMed,
            }}><Link href="/connect_four_page">Medium</Link></button>
      <button type = "submit"
            onClick={() => toggleColorHard(colorHard, setColorHard)}
            className="hard_btn"
            style={{
              backgroundColor: colorHard,
            }}><Link href="/connect_four_page">Hard</Link></button>
      </div>
    </div>
    
  );
}
