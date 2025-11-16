import random
import numpy as np
from typing import Tuple, List, Optional
from game.minesweeper import Minesweeper, CellState, GameState

class MinesweeperAgent:
    """
    Base AI agent for playing Minesweeper.
    Starts with simple rule-based logic that can be extended with ML later.
    """
    
    def __init__(self, game: Minesweeper):
        self.game = game
        self.knowledge_base = []  # Store logical constraints
        
    def get_safe_cells(self) -> List[Tuple[int, int]]:
        """Get cells that are definitely safe based on revealed information"""
        safe_cells = []
        
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                if self.game.get_cell_state(row, col) == CellState.REVEALED:
                    # Check neighbors of revealed cells
                    neighbors = self._get_neighbors(row, col)
                    hidden_neighbors = [
                        (r, c) for r, c in neighbors 
                        if self.game.get_cell_state(r, c) == CellState.HIDDEN
                    ]
                    flagged_neighbors = [
                        (r, c) for r, c in neighbors 
                        if self.game.get_cell_state(r, c) == CellState.FLAGGED
                    ]
                    
                    cell_value = self.game.get_cell_value(row, col)
                    
                    # If all mines around this cell are flagged, hidden neighbors are safe
                    if len(flagged_neighbors) == cell_value and hidden_neighbors:
                        safe_cells.extend(hidden_neighbors)
        
        return list(set(safe_cells))  # Remove duplicates
    
    def get_mine_cells(self) -> List[Tuple[int, int]]:
        """Get cells that are definitely mines based on revealed information"""
        mine_cells = []
        
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                if self.game.get_cell_state(row, col) == CellState.REVEALED:
                    neighbors = self._get_neighbors(row, col)
                    hidden_neighbors = [
                        (r, c) for r, c in neighbors 
                        if self.game.get_cell_state(r, c) == CellState.HIDDEN
                    ]
                    flagged_neighbors = [
                        (r, c) for r, c in neighbors 
                        if self.game.get_cell_state(r, c) == CellState.FLAGGED
                    ]
                    
                    cell_value = self.game.get_cell_value(row, col)
                    
                    # If hidden + flagged = cell value, all hidden are mines
                    if len(hidden_neighbors) + len(flagged_neighbors) == cell_value and hidden_neighbors:
                        mine_cells.extend(hidden_neighbors)
        
        return list(set(mine_cells))  # Remove duplicates
    
    def _get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Get all valid neighboring cells"""
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.game.rows and 0 <= nc < self.game.cols:
                    neighbors.append((nr, nc))
        return neighbors
    
    def choose_action(self) -> Optional[Tuple[str, int, int]]:
        """
        Choose the next action to take.
        Returns: (action_type, row, col) where action_type is 'reveal' or 'flag'
                 or None if no action available
        """
        # Strategy 1: Flag cells that are definitely mines
        mine_cells = self.get_mine_cells()
        for row, col in mine_cells:
            if self.game.get_cell_state(row, col) == CellState.HIDDEN:
                return ('flag', row, col)
        
        # Strategy 2: Reveal cells that are definitely safe
        safe_cells = self.get_safe_cells()
        if safe_cells:
            row, col = safe_cells[0]
            return ('reveal', row, col)
        
        # Strategy 3: If no certain moves, make an educated guess
        # Find cells with lowest mine probability
        hidden_cells = []
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                if self.game.get_cell_state(row, col) == CellState.HIDDEN:
                    hidden_cells.append((row, col))
        
        if hidden_cells:
            # Simple heuristic: prefer cells with more revealed neighbors
            # (they're more likely to be informed guesses)
            best_cell = None
            max_revealed_neighbors = -1
            
            for row, col in hidden_cells:
                neighbors = self._get_neighbors(row, col)
                revealed_count = sum(
                    1 for r, c in neighbors 
                    if self.game.get_cell_state(r, c) == CellState.REVEALED
                )
                
                if revealed_count > max_revealed_neighbors:
                    max_revealed_neighbors = revealed_count
                    best_cell = (row, col)
            
            # If no revealed neighbors anywhere, pick a random cell
            if max_revealed_neighbors == 0:
                # Prefer corners and edges for first moves
                corner_cells = [
                    (0, 0), (0, self.game.cols - 1),
                    (self.game.rows - 1, 0), (self.game.rows - 1, self.game.cols - 1)
                ]
                available_corners = [c for c in corner_cells if c in hidden_cells]
                if available_corners:
                    best_cell = random.choice(available_corners)
                else:
                    best_cell = random.choice(hidden_cells)
            
            return ('reveal', best_cell[0], best_cell[1])
        
        return None
    
    def get_board_state(self) -> np.ndarray:
        """
        Get current board state as numpy array for ML training later.
        Returns array where:
        - -1: hidden cell
        - -2: flagged cell
        - 0-8: revealed cell with number
        - 9: revealed mine (when game over)
        """
        state = np.zeros((self.game.rows, self.game.cols), dtype=np.int8)
        
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                cell_state = self.game.get_cell_state(row, col)
                
                if cell_state == CellState.HIDDEN:
                    state[row, col] = -1
                elif cell_state == CellState.FLAGGED:
                    state[row, col] = -2
                elif cell_state == CellState.REVEALED:
                    if self.game.is_mine(row, col):
                        state[row, col] = 9
                    else:
                        state[row, col] = self.game.get_cell_value(row, col)
        
        return state
    
    def calculate_statistics(self) -> dict:
        """Calculate current game statistics"""
        total_cells = self.game.rows * self.game.cols
        revealed_cells = sum(
            1 for row in range(self.game.rows) 
            for col in range(self.game.cols)
            if self.game.get_cell_state(row, col) == CellState.REVEALED
        )
        flagged_cells = sum(
            1 for row in range(self.game.rows) 
            for col in range(self.game.cols)
            if self.game.get_cell_state(row, col) == CellState.FLAGGED
        )
        
        return {
            'total_cells': total_cells,
            'revealed_cells': revealed_cells,
            'flagged_cells': flagged_cells,
            'progress': revealed_cells / (total_cells - self.game.num_mines) * 100,
            'flags_correct': flagged_cells <= self.game.num_mines
        }


class RandomAgent(MinesweeperAgent):
    """
    Simple random agent for baseline comparison.
    Just clicks random hidden cells.
    """
    
    def choose_action(self) -> Optional[Tuple[str, int, int]]:
        """Choose a random hidden cell to reveal"""
        hidden_cells = []
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                if self.game.get_cell_state(row, col) == CellState.HIDDEN:
                    hidden_cells.append((row, col))
        
        if hidden_cells:
            row, col = random.choice(hidden_cells)
            return ('reveal', row, col)
        
        return None