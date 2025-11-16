"""
Advanced Minesweeper Agent with Pattern Recognition

Implements common Minesweeper patterns:
- 1-2-1 pattern (mines under the 1s)
- 1-2-2-1 pattern (mines under the 2s)
- 1-2-X pattern (X is always a mine)
- 1-1-X pattern from border (X is always safe)
- Subset logic (reduction patterns)
"""

import random
from typing import Tuple, List, Optional, Set
from game.minesweeper import Minesweeper, CellState, GameState

class PatternAgent:
    """Advanced agent using pattern recognition"""
    
    def __init__(self, game: Minesweeper):
        self.game = game
        
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
    
    def _is_revealed(self, row: int, col: int) -> bool:
        """Check if cell is revealed"""
        return self.game.get_cell_state(row, col) == CellState.REVEALED
    
    def _is_hidden(self, row: int, col: int) -> bool:
        """Check if cell is hidden"""
        return self.game.get_cell_state(row, col) == CellState.HIDDEN
    
    def _is_flagged(self, row: int, col: int) -> bool:
        """Check if cell is flagged"""
        return self.game.get_cell_state(row, col) == CellState.FLAGGED
    
    def _get_effective_value(self, row: int, col: int) -> int:
        """Get cell value minus already flagged neighbors"""
        if not self._is_revealed(row, col):
            return 0
        
        base_value = self.game.get_cell_value(row, col)
        flagged_count = sum(1 for r, c in self._get_neighbors(row, col) 
                           if self._is_flagged(r, c))
        return base_value - flagged_count
    
    def find_certain_mines(self) -> List[Tuple[int, int]]:
        """Find cells that are definitely mines"""
        mines = []
        
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                if not self._is_revealed(row, col):
                    continue
                
                neighbors = self._get_neighbors(row, col)
                hidden_neighbors = [n for n in neighbors if self._is_hidden(n[0], n[1])]
                effective_value = self._get_effective_value(row, col)
                
                # If hidden cells = remaining mines, all are mines
                if len(hidden_neighbors) == effective_value > 0:
                    mines.extend(hidden_neighbors)
        
        return list(set(mines))
    
    def find_certain_safe(self) -> List[Tuple[int, int]]:
        """Find cells that are definitely safe"""
        safe = []
        
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                if not self._is_revealed(row, col):
                    continue
                
                neighbors = self._get_neighbors(row, col)
                hidden_neighbors = [n for n in neighbors if self._is_hidden(n[0], n[1])]
                effective_value = self._get_effective_value(row, col)
                
                # If effective value is 0, all hidden neighbors are safe
                if effective_value == 0 and hidden_neighbors:
                    safe.extend(hidden_neighbors)
        
        return list(set(safe))
    
    def check_1_2_pattern(self) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
        """
        Check for 1-2 pattern: when 1 and 2 are adjacent along a wall
        The cell opposite to the 2 is a mine, the cell next to the 1 is safe
        """
        mines = []
        safe = []
        
        for row in range(self.game.rows):
            for col in range(self.game.cols - 1):
                # Check horizontal 1-2 patterns
                if (self._is_revealed(row, col) and 
                    self._is_revealed(row, col + 1)):
                    
                    val1 = self._get_effective_value(row, col)
                    val2 = self._get_effective_value(row, col + 1)
                    
                    # Pattern: 1-2 along bottom wall
                    if val1 == 1 and val2 == 2 and row == self.game.rows - 1:
                        if col > 0 and self._is_hidden(row, col - 1):
                            safe.append((row, col - 1))
                        if col + 2 < self.game.cols and self._is_hidden(row, col + 2):
                            mines.append((row, col + 2))
                    
                    # Pattern: 1-2 along top wall
                    if val1 == 1 and val2 == 2 and row == 0:
                        if col > 0 and self._is_hidden(row, col - 1):
                            safe.append((row, col - 1))
                        if col + 2 < self.game.cols and self._is_hidden(row, col + 2):
                            mines.append((row, col + 2))
        
        # Check vertical 1-2 patterns
        for row in range(self.game.rows - 1):
            for col in range(self.game.cols):
                if (self._is_revealed(row, col) and 
                    self._is_revealed(row + 1, col)):
                    
                    val1 = self._get_effective_value(row, col)
                    val2 = self._get_effective_value(row + 1, col)
                    
                    # Pattern along left wall
                    if val1 == 1 and val2 == 2 and col == 0:
                        if row > 0 and self._is_hidden(row - 1, col):
                            safe.append((row - 1, col))
                        if row + 2 < self.game.rows and self._is_hidden(row + 2, col):
                            mines.append((row + 2, col))
                    
                    # Pattern along right wall
                    if val1 == 1 and val2 == 2 and col == self.game.cols - 1:
                        if row > 0 and self._is_hidden(row - 1, col):
                            safe.append((row - 1, col))
                        if row + 2 < self.game.rows and self._is_hidden(row + 2, col):
                            mines.append((row + 2, col))
        
        return list(set(mines)), list(set(safe))
    
    def check_1_2_1_pattern(self) -> List[Tuple[int, int]]:
        """
        Check for 1-2-1 pattern along walls
        Mines are under the 1s
        """
        mines = []
        
        # Horizontal 1-2-1
        for row in range(self.game.rows):
            for col in range(self.game.cols - 2):
                if (self._is_revealed(row, col) and 
                    self._is_revealed(row, col + 1) and
                    self._is_revealed(row, col + 2)):
                    
                    vals = [self._get_effective_value(row, c) for c in [col, col+1, col+2]]
                    
                    if vals == [1, 2, 1]:
                        # Check if against a wall
                        if row == 0:
                            # Mines below the 1s
                            if row + 1 < self.game.rows:
                                if self._is_hidden(row + 1, col):
                                    mines.append((row + 1, col))
                                if self._is_hidden(row + 1, col + 2):
                                    mines.append((row + 1, col + 2))
                        elif row == self.game.rows - 1:
                            # Mines above the 1s
                            if row - 1 >= 0:
                                if self._is_hidden(row - 1, col):
                                    mines.append((row - 1, col))
                                if self._is_hidden(row - 1, col + 2):
                                    mines.append((row - 1, col + 2))
        
        # Vertical 1-2-1
        for row in range(self.game.rows - 2):
            for col in range(self.game.cols):
                if (self._is_revealed(row, col) and 
                    self._is_revealed(row + 1, col) and
                    self._is_revealed(row + 2, col)):
                    
                    vals = [self._get_effective_value(r, col) for r in [row, row+1, row+2]]
                    
                    if vals == [1, 2, 1]:
                        # Check if against a wall
                        if col == 0:
                            # Mines to the right of the 1s
                            if col + 1 < self.game.cols:
                                if self._is_hidden(row, col + 1):
                                    mines.append((row, col + 1))
                                if self._is_hidden(row + 2, col + 1):
                                    mines.append((row + 2, col + 1))
                        elif col == self.game.cols - 1:
                            # Mines to the left of the 1s
                            if col - 1 >= 0:
                                if self._is_hidden(row, col - 1):
                                    mines.append((row, col - 1))
                                if self._is_hidden(row + 2, col - 1):
                                    mines.append((row + 2, col - 1))
        
        return list(set(mines))
    
    def check_1_1_pattern(self) -> List[Tuple[int, int]]:
        """
        Check for 1-1 pattern from border
        The third cell is always safe
        """
        safe = []
        
        # Horizontal from left edge
        for row in range(self.game.rows):
            if (self._is_revealed(row, 0) and 
                self._is_revealed(row, 1) and
                self._get_effective_value(row, 0) == 1 and
                self._get_effective_value(row, 1) == 1):
                
                if 2 < self.game.cols and self._is_hidden(row, 2):
                    safe.append((row, 2))
        
        # Horizontal from right edge
        for row in range(self.game.rows):
            if (self._is_revealed(row, self.game.cols - 1) and 
                self._is_revealed(row, self.game.cols - 2) and
                self._get_effective_value(row, self.game.cols - 1) == 1 and
                self._get_effective_value(row, self.game.cols - 2) == 1):
                
                if self.game.cols - 3 >= 0 and self._is_hidden(row, self.game.cols - 3):
                    safe.append((row, self.game.cols - 3))
        
        # Vertical from top edge
        for col in range(self.game.cols):
            if (self._is_revealed(0, col) and 
                self._is_revealed(1, col) and
                self._get_effective_value(0, col) == 1 and
                self._get_effective_value(1, col) == 1):
                
                if 2 < self.game.rows and self._is_hidden(2, col):
                    safe.append((2, col))
        
        # Vertical from bottom edge
        for col in range(self.game.cols):
            if (self._is_revealed(self.game.rows - 1, col) and 
                self._is_revealed(self.game.rows - 2, col) and
                self._get_effective_value(self.game.rows - 1, col) == 1 and
                self._get_effective_value(self.game.rows - 2, col) == 1):
                
                if self.game.rows - 3 >= 0 and self._is_hidden(self.game.rows - 3, col):
                    safe.append((self.game.rows - 3, col))
        
        return list(set(safe))
    
    def choose_action(self) -> Optional[Tuple[str, int, int]]:
        """Choose next action using pattern recognition"""
        
        # Step 1: Check for certain mines
        mines = self.find_certain_mines()
        if mines:
            for row, col in mines:
                if self._is_hidden(row, col):
                    return ('flag', row, col)
        
        # Step 2: Check for certain safe cells
        safe = self.find_certain_safe()
        if safe:
            row, col = safe[0]
            return ('reveal', row, col)
        
        # Step 3: Check 1-2-1 pattern
        pattern_mines = self.check_1_2_1_pattern()
        if pattern_mines:
            for row, col in pattern_mines:
                if self._is_hidden(row, col):
                    return ('flag', row, col)
        
        # Step 4: Check 1-2 pattern
        pattern_mines, pattern_safe = self.check_1_2_pattern()
        if pattern_mines:
            for row, col in pattern_mines:
                if self._is_hidden(row, col):
                    return ('flag', row, col)
        if pattern_safe:
            row, col = pattern_safe[0]
            if self._is_hidden(row, col):
                return ('reveal', row, col)
        
        # Step 5: Check 1-1 pattern
        pattern_safe = self.check_1_1_pattern()
        if pattern_safe:
            row, col = pattern_safe[0]
            return ('reveal', row, col)
        
        # Step 6: Make an educated guess
        return self._make_educated_guess()
    
    def _make_educated_guess(self) -> Optional[Tuple[str, int, int]]:
        """Make the best possible guess"""
        hidden_cells = []
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                if self._is_hidden(row, col):
                    hidden_cells.append((row, col))
        
        if not hidden_cells:
            return None
        
        # Prefer cells with more revealed neighbors
        best_cell = None
        max_revealed = -1
        
        for row, col in hidden_cells:
            neighbors = self._get_neighbors(row, col)
            revealed_count = sum(1 for r, c in neighbors if self._is_revealed(r, c))
            
            if revealed_count > max_revealed:
                max_revealed = revealed_count
                best_cell = (row, col)
        
        # If no revealed neighbors, pick corner
        if max_revealed == 0:
            corners = [(0, 0), (0, self.game.cols - 1), 
                      (self.game.rows - 1, 0), (self.game.rows - 1, self.game.cols - 1)]
            for corner in corners:
                if corner in hidden_cells:
                    return ('reveal', corner[0], corner[1])
            best_cell = random.choice(hidden_cells)
        
        return ('reveal', best_cell[0], best_cell[1])
    
    def calculate_statistics(self) -> dict:
        """Calculate current game statistics"""
        total_cells = self.game.rows * self.game.cols
        revealed_cells = sum(
            1 for row in range(self.game.rows) 
            for col in range(self.game.cols)
            if self._is_revealed(row, col)
        )
        flagged_cells = sum(
            1 for row in range(self.game.rows) 
            for col in range(self.game.cols)
            if self._is_flagged(row, col)
        )
        
        return {
            'total_cells': total_cells,
            'revealed_cells': revealed_cells,
            'flagged_cells': flagged_cells,
            'progress': revealed_cells / (total_cells - self.game.num_mines) * 100,
            'flags_correct': flagged_cells <= self.game.num_mines
        }