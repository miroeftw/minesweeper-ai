"""
AI Demo - Watch the AI agent play Minesweeper

This script lets you watch different AI agents play the game.
"""

from game.ui import MinesweeperUI
from game.minesweeper import Difficulty
from ai.agent import MinesweeperAgent, RandomAgent
from ai.pattern_agent import PatternAgent

def main():
    print("="*60)
    print("MINESWEEPER AI DEMO")
    print("="*60)
    print("\nChoose AI Agent:")
    print("1. Pattern Agent (Advanced - uses 1-2-1, 1-1, etc.)")
    print("2. Smart Agent (Basic rule-based logic)")
    print("3. Random Agent (Baseline - just random clicks)")
    print("\nChoose Difficulty:")
    print("a. Beginner (8x8, 10 mines)")
    print("b. Intermediate (16x16, 40 mines)")
    print("c. Expert (16x30, 99 mines)")
    print("\n" + "="*60)
    
    # Get agent choice
    agent_choice = input("\nSelect agent (1, 2, or 3) [default: 1]: ").strip() or "1"
    
    # Get difficulty
    diff_choice = input("Select difficulty (a, b, or c) [default: a]: ").strip().lower() or "a"
    
    difficulty_map = {
        'a': Difficulty.BEGINNER,
        'b': Difficulty.INTERMEDIATE,
        'c': Difficulty.EXPERT
    }
    difficulty = difficulty_map.get(diff_choice, Difficulty.BEGINNER)
    
    # Get game settings
    delay = input("Delay between moves in ms [default: 200]: ").strip()
    delay = int(delay) if delay.isdigit() else 200
    
    auto_restart = input("Auto-restart after game ends? (y/n) [default: y]: ").strip().lower()
    auto_restart = auto_restart != 'n'
    
    max_games = input("Max games to play (0 = infinite) [default: 10]: ").strip()
    max_games = int(max_games) if max_games.isdigit() else 10
    
    print("\n" + "="*60)
    print("STARTING AI GAME")
    print("="*60)
    print("Controls during game:")
    print("  SPACE: Pause/Resume")
    print("  R: Manual restart")
    print("  L: View leaderboard")
    print("  ESC: Quit")
    print("="*60 + "\n")
    
    # Create game UI
    ui = MinesweeperUI(difficulty)
    
    # Create agent
    if agent_choice == "3":
        print("🤖 Using Random Agent (baseline)")
        agent = RandomAgent(ui.game)
    elif agent_choice == "2":
        print("🧠 Using Smart Agent (basic rules)")
        agent = MinesweeperAgent(ui.game)
    else:
        print("🎯 Using Pattern Agent (advanced patterns)")
        agent = PatternAgent(ui.game)
    
    # Run with AI
    ui.run_with_ai(
        agent=agent,
        delay_ms=delay,
        auto_restart=auto_restart,
        max_games=max_games
    )
    
    print("\nThanks for watching! 👋")

if __name__ == "__main__":
    main()