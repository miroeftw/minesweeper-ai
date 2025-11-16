from game.ui import MinesweeperUI
from game.minesweeper import Difficulty

def main():
    """
    Main entry point for Minesweeper game
    
    Keyboard shortcuts:
    - 1: Beginner (8x8, 10 mines)
    - 2: Intermediate (16x16, 40 mines)
    - 3: Expert (16x30, 99 mines)
    
    Mouse controls:
    - Left click: Reveal cell
    - Right click: Place/remove flag
    - Click smiley: Restart game
    """
    print("Starting Minesweeper...")
    print("Keyboard shortcuts: 1=Beginner, 2=Intermediate, 3=Expert")
    print("Mouse: Left-click to reveal, Right-click to flag")
    
    # Start with Beginner difficulty
    game = MinesweeperUI(Difficulty.EXPERT)
    game.run()
    
    print("Thanks for playing!")

if __name__ == "__main__":
    main()