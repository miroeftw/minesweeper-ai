import random
from enum import Enum
from typing import List, Tuple, Set

class CellState(Enum):
    HIDDEN = 0
    REVEALED = 1
    FLAGGED = 2

class GameState(Enum):
    READY = 0  # Before first click
    PLAYING = 1
    WON = 2
    LOST = 3

class Difficulty(Enum):
    BEGINNER = (8, 8, 10)      # rows, cols, mines
    INTERMEDIATE = (16, 16, 40)
    EXPERT = (16, 30, 99)

class Minesweeper:
    def __init__(self, difficulty: Difficulty = Difficulty.BEGINNER):
        self.rows, self.cols, self.num_mines = difficulty.value
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.cell_states = [[CellState.HIDDEN for _ in range(self.cols)] for _ in range(self.rows)]
        self.mines: Set[Tuple[int, int]] = set()
        self.game_state = GameState.READY
        self.flags_placed = 0
        self.cells_revealed = 0
        self.first_click = True
        
    def _generate_mines(self, exclude_row: int, exclude_col: int):
        """Generate mines, excluding the first clicked cell and its neighbors"""
        excluded_cells = self._get_neighbors(exclude_row, exclude_col)
        excluded_cells.add((exclude_row, exclude_col))
        
        available_cells = [
            (r, c) for r in range(self.rows) for c in range(self.cols)
            if (r, c) not in excluded_cells
        ]
        
        self.mines = set(random.sample(available_cells, self.num_mines))
        
        # Calculate numbers
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) not in self.mines:
                    self.board[r][c] = self._count_adjacent_mines(r, c)
    
    def _get_neighbors(self, row: int, col: int) -> Set[Tuple[int, int]]:
        """Get all valid neighboring cells"""
        neighbors = set()
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    neighbors.add((nr, nc))
        return neighbors
    
    def _count_adjacent_mines(self, row: int, col: int) -> int:
        """Count mines in neighboring cells"""
        return sum(1 for r, c in self._get_neighbors(row, col) if (r, c) in self.mines)
    
    def reveal_cell(self, row: int, col: int) -> bool:
        """
        Reveal a cell. Returns True if game continues, False if mine hit.
        """
        if self.game_state in [GameState.WON, GameState.LOST]:
            return False
        
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return True
        
        # Generate mines on first click
        if self.first_click:
            self._generate_mines(row, col)
            self.first_click = False
            self.game_state = GameState.PLAYING
        
        # Can't reveal flagged or already revealed cells
        if self.cell_states[row][col] != CellState.HIDDEN:
            return True
        
        # Hit a mine!
        if (row, col) in self.mines:
            self.cell_states[row][col] = CellState.REVEALED
            self.game_state = GameState.LOST
            return False
        
        # Reveal cell
        self._reveal_recursive(row, col)
        
        # Check win condition
        if self.cells_revealed == (self.rows * self.cols - self.num_mines):
            self.game_state = GameState.WON
        
        return True
    
    def _reveal_recursive(self, row: int, col: int):
        """Recursively reveal cells (flood fill for empty cells)"""
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return
        
        if self.cell_states[row][col] != CellState.HIDDEN:
            return
        
        if (row, col) in self.mines:
            return
        
        self.cell_states[row][col] = CellState.REVEALED
        self.cells_revealed += 1
        
        # If cell is empty (0), reveal neighbors
        if self.board[row][col] == 0:
            for nr, nc in self._get_neighbors(row, col):
                self._reveal_recursive(nr, nc)
    
    def toggle_flag(self, row: int, col: int):
        """Toggle flag on a cell"""
        if self.game_state in [GameState.WON, GameState.LOST]:
            return
        
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return
        
        if self.cell_states[row][col] == CellState.REVEALED:
            return
        
        if self.cell_states[row][col] == CellState.HIDDEN:
            self.cell_states[row][col] = CellState.FLAGGED
            self.flags_placed += 1
        elif self.cell_states[row][col] == CellState.FLAGGED:
            self.cell_states[row][col] = CellState.HIDDEN
            self.flags_placed -= 1
    
    def get_remaining_mines(self) -> int:
        """Get count of remaining mines (total - flags placed)"""
        return self.num_mines - self.flags_placed
    
    def reset(self, difficulty: Difficulty = None):
        """Reset the game"""
        if difficulty:
            self.rows, self.cols, self.num_mines = difficulty.value
        
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.cell_states = [[CellState.HIDDEN for _ in range(self.cols)] for _ in range(self.rows)]
        self.mines = set()
        self.game_state = GameState.READY
        self.flags_placed = 0
        self.cells_revealed = 0
        self.first_click = True
    
    def is_mine(self, row: int, col: int) -> bool:
        """Check if a cell contains a mine"""
        return (row, col) in self.mines
    
    def get_cell_value(self, row: int, col: int) -> int:
        """Get the number in a cell (0-8)"""
        return self.board[row][col]
    
    def get_cell_state(self, row: int, col: int) -> CellState:
        """Get the state of a cell"""
        return self.cell_states[row][col]