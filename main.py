from game.ui import MinesweeperUI
from game.minesweeper import Difficulty

def main():
    """
    Main entry point for Minesweeper game
    
    Keyboard shortcuts:
    - 1: Beginner (8x8, 10 mines)
    - 2: Intermediate (16x16, 40 mines)
    - 3: Expert (16x30, 99 mines)
    - L: View Leaderboard
    
    Mouse controls:
    - Left click: Reveal cell
    - Right click: Place/remove flag
    - Click smiley: Restart game
    """
    print("Starting Minesweeper...")
    print("Keyboard shortcuts: 1=Beginner, 2=Intermediate, 3=Expert, L=Leaderboard")
    print("Mouse: Left-click to reveal, Right-click to flag")
    print("Try to beat the leaderboard times!")
    
    # Start with Beginner difficulty
    game = MinesweeperUI(Difficulty.BEGINNER)
    game.run()
    
    print("Thanks for playing!")

if __name__ == "__main__":
    main()