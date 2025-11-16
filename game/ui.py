import pygame
import time
from game.minesweeper import Minesweeper, CellState, GameState, Difficulty

# Colors (GNOME Mines inspired)
COLORS = {
    'bg': (192, 192, 192),
    'cell_hidden': (189, 189, 189),
    'cell_revealed': (225, 225, 225),
    'cell_highlight': (230, 230, 230),
    'border_light': (255, 255, 255),
    'border_dark': (128, 128, 128),
    'border_darker': (64, 64, 64),
    'mine': (0, 0, 0),
    'mine_bg_hit': (255, 0, 0),
    'flag': (255, 0, 0),
    'text': (0, 0, 0),
    'header_bg': (192, 192, 192),
    'counter_bg': (0, 0, 0),
    'counter_text': (255, 0, 0),
}

# Number colors (like GNOME Mines)
NUMBER_COLORS = {
    1: (0, 0, 255),      # Blue
    2: (0, 128, 0),      # Green
    3: (255, 0, 0),      # Red
    4: (0, 0, 128),      # Dark Blue
    5: (128, 0, 0),      # Dark Red
    6: (0, 128, 128),    # Cyan
    7: (0, 0, 0),        # Black
    8: (128, 128, 128),  # Gray
}

class MinesweeperUI:
    def __init__(self, difficulty: Difficulty = Difficulty.BEGINNER):
        pygame.init()
        
        self.game = Minesweeper(difficulty)
        self.current_difficulty = difficulty
        
        # UI Constants
        self.cell_size = 32
        self.header_height = 80
        self.border_width = 10
        
        # Calculate window size
        self.board_width = self.game.cols * self.cell_size
        self.board_height = self.game.rows * self.cell_size
        self.window_width = self.board_width + 2 * self.border_width
        self.window_height = self.board_height + self.header_height + 2 * self.border_width
        
        # Create window
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Minesweeper")
        
        # Fonts
        self.font_large = pygame.font.Font(None, 40)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Timer
        self.start_time = None
        self.elapsed_time = 0
        
        # Smiley button
        self.smiley_rect = pygame.Rect(
            self.window_width // 2 - 25,
            20,
            50,
            50
        )
        
        self.running = True
        self.clock = pygame.time.Clock()
    
    def draw_3d_rect(self, surface, rect, raised=True):
        """Draw a 3D beveled rectangle"""
        x, y, w, h = rect
        
        if raised:
            # Light border (top-left)
            pygame.draw.line(surface, COLORS['border_light'], (x, y), (x + w, y), 2)
            pygame.draw.line(surface, COLORS['border_light'], (x, y), (x, y + h), 2)
            # Dark border (bottom-right)
            pygame.draw.line(surface, COLORS['border_darker'], (x + w, y), (x + w, y + h), 2)
            pygame.draw.line(surface, COLORS['border_darker'], (x, y + h), (x + w, y + h), 2)
            # Medium border
            pygame.draw.line(surface, COLORS['border_dark'], (x + w - 1, y + 1), (x + w - 1, y + h - 1), 1)
            pygame.draw.line(surface, COLORS['border_dark'], (x + 1, y + h - 1), (x + w - 1, y + h - 1), 1)
        else:
            # Inverted (pressed)
            pygame.draw.line(surface, COLORS['border_darker'], (x, y), (x + w, y), 2)
            pygame.draw.line(surface, COLORS['border_darker'], (x, y), (x, y + h), 2)
            pygame.draw.line(surface, COLORS['border_light'], (x + w, y), (x + w, y + h), 2)
            pygame.draw.line(surface, COLORS['border_light'], (x, y + h), (x + w, y + h), 2)
    
    def draw_mine(self, surface, x, y, size):
        """Draw a mine"""
        center_x, center_y = x + size // 2, y + size // 2
        radius = size // 4
        
        # Main circle
        pygame.draw.circle(surface, COLORS['mine'], (center_x, center_y), radius)
        
        # Spikes
        spike_length = radius + 4
        for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
            import math
            rad = math.radians(angle)
            end_x = center_x + int(spike_length * math.cos(rad))
            end_y = center_y + int(spike_length * math.sin(rad))
            pygame.draw.line(surface, COLORS['mine'], (center_x, center_y), (end_x, end_y), 2)
        
        # Highlight
        pygame.draw.circle(surface, (255, 255, 255), (center_x - 3, center_y - 3), 3)
    
    def draw_flag(self, surface, x, y, size):
        """Draw a flag"""
        pole_x = x + size // 2
        pole_top = y + size // 4
        pole_bottom = y + 3 * size // 4
        
        # Pole
        pygame.draw.line(surface, COLORS['text'], (pole_x, pole_top), (pole_x, pole_bottom), 2)
        
        # Flag
        flag_points = [
            (pole_x, pole_top),
            (pole_x + size // 3, pole_top + size // 6),
            (pole_x, pole_top + size // 3)
        ]
        pygame.draw.polygon(surface, COLORS['flag'], flag_points)
    
    def draw_cell(self, row, col):
        """Draw a single cell"""
        x = self.border_width + col * self.cell_size
        y = self.header_height + self.border_width + row * self.cell_size
        rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
        
        cell_state = self.game.get_cell_state(row, col)
        
        if cell_state == CellState.HIDDEN:
            # Draw raised button
            pygame.draw.rect(self.screen, COLORS['cell_hidden'], rect)
            self.draw_3d_rect(self.screen, rect, raised=True)
            
        elif cell_state == CellState.FLAGGED:
            # Draw raised button with flag
            pygame.draw.rect(self.screen, COLORS['cell_hidden'], rect)
            self.draw_3d_rect(self.screen, rect, raised=True)
            self.draw_flag(self.screen, x, y, self.cell_size)
            
        elif cell_state == CellState.REVEALED:
            # Draw flat revealed cell
            if self.game.is_mine(row, col):
                # Mine hit
                bg_color = COLORS['mine_bg_hit'] if self.game.game_state == GameState.LOST else COLORS['cell_revealed']
                pygame.draw.rect(self.screen, bg_color, rect)
                self.draw_mine(self.screen, x, y, self.cell_size)
            else:
                pygame.draw.rect(self.screen, COLORS['cell_revealed'], rect)
                self.draw_3d_rect(self.screen, rect, raised=False)
                
                # Draw number
                value = self.game.get_cell_value(row, col)
                if value > 0:
                    color = NUMBER_COLORS.get(value, COLORS['text'])
                    text = self.font_medium.render(str(value), True, color)
                    text_rect = text.get_rect(center=(x + self.cell_size // 2, y + self.cell_size // 2))
                    self.screen.blit(text, text_rect)
        
        # Draw grid lines
        pygame.draw.rect(self.screen, COLORS['border_dark'], rect, 1)
    
    def draw_counter(self, x, y, value):
        """Draw a digital counter display"""
        rect = pygame.Rect(x, y, 80, 40)
        pygame.draw.rect(self.screen, COLORS['counter_bg'], rect)
        self.draw_3d_rect(self.screen, rect, raised=False)
        
        text = self.font_large.render(f"{value:03d}", True, COLORS['counter_text'])
        text_rect = text.get_rect(center=(x + 40, y + 20))
        self.screen.blit(text, text_rect)
    
    def draw_smiley(self):
        """Draw the smiley face button"""
        pygame.draw.rect(self.screen, COLORS['cell_hidden'], self.smiley_rect)
        self.draw_3d_rect(self.screen, self.smiley_rect, raised=True)
        
        # Draw face based on game state
        center_x, center_y = self.smiley_rect.center
        
        # Face
        pygame.draw.circle(self.screen, (255, 255, 0), (center_x, center_y), 18)
        pygame.draw.circle(self.screen, COLORS['text'], (center_x, center_y), 18, 2)
        
        # Eyes
        if self.game.game_state == GameState.LOST:
            # X eyes
            pygame.draw.line(self.screen, COLORS['text'], (center_x - 10, center_y - 5), (center_x - 6, center_y - 1), 2)
            pygame.draw.line(self.screen, COLORS['text'], (center_x - 6, center_y - 5), (center_x - 10, center_y - 1), 2)
            pygame.draw.line(self.screen, COLORS['text'], (center_x + 6, center_y - 5), (center_x + 10, center_y - 1), 2)
            pygame.draw.line(self.screen, COLORS['text'], (center_x + 10, center_y - 5), (center_x + 6, center_y - 1), 2)
            # Frown
            pygame.draw.arc(self.screen, COLORS['text'], (center_x - 10, center_y + 5, 20, 10), 3.14, 6.28, 2)
        elif self.game.game_state == GameState.WON:
            # Sunglasses eyes
            pygame.draw.rect(self.screen, COLORS['text'], (center_x - 12, center_y - 6, 8, 4))
            pygame.draw.rect(self.screen, COLORS['text'], (center_x + 4, center_y - 6, 8, 4))
            # Big smile
            pygame.draw.arc(self.screen, COLORS['text'], (center_x - 10, center_y - 5, 20, 20), 3.14, 6.28, 2)
        else:
            # Normal eyes
            pygame.draw.circle(self.screen, COLORS['text'], (center_x - 8, center_y - 3), 2)
            pygame.draw.circle(self.screen, COLORS['text'], (center_x + 8, center_y - 3), 2)
            # Smile
            pygame.draw.arc(self.screen, COLORS['text'], (center_x - 8, center_y - 2, 16, 16), 3.14, 6.28, 2)
    
    def draw_header(self):
        """Draw the header with counters and smiley"""
        header_rect = pygame.Rect(0, 0, self.window_width, self.header_height)
        pygame.draw.rect(self.screen, COLORS['header_bg'], header_rect)
        
        # Mine counter (left)
        self.draw_counter(20, 20, max(0, self.game.get_remaining_mines()))
        
        # Timer (right)
        if self.game.game_state == GameState.PLAYING:
            if self.start_time is None:
                self.start_time = time.time()
            self.elapsed_time = int(time.time() - self.start_time)
        elif self.game.game_state == GameState.READY:
            self.elapsed_time = 0
            self.start_time = None
        
        self.draw_counter(self.window_width - 100, 20, min(999, self.elapsed_time))
        
        # Smiley button (center)
        self.draw_smiley()
    
    def draw_board(self):
        """Draw the entire game board"""
        for row in range(self.game.rows):
            for col in range(self.game.cols):
                self.draw_cell(row, col)
    
    def get_cell_from_pos(self, pos):
        """Convert mouse position to cell coordinates"""
        x, y = pos
        col = (x - self.border_width) // self.cell_size
        row = (y - self.header_height - self.border_width) // self.cell_size
        
        if 0 <= row < self.game.rows and 0 <= col < self.game.cols:
            return row, col
        return None
    
    def handle_click(self, pos, button):
        """Handle mouse click"""
        # Check smiley button
        if self.smiley_rect.collidepoint(pos):
            self.game.reset(self.current_difficulty)
            self.start_time = None
            self.elapsed_time = 0
            return
        
        # Check board click
        cell = self.get_cell_from_pos(pos)
        if cell:
            row, col = cell
            if button == 1:  # Left click
                self.game.reveal_cell(row, col)
            elif button == 3:  # Right click
                self.game.toggle_flag(row, col)
    
    def run(self):
        """Main game loop"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos, event.button)
                elif event.type == pygame.KEYDOWN:
                    # Keyboard shortcuts for difficulty
                    if event.key == pygame.K_1:
                        self.change_difficulty(Difficulty.BEGINNER)
                    elif event.key == pygame.K_2:
                        self.change_difficulty(Difficulty.INTERMEDIATE)
                    elif event.key == pygame.K_3:
                        self.change_difficulty(Difficulty.EXPERT)
            
            # Draw everything
            self.screen.fill(COLORS['bg'])
            self.draw_header()
            self.draw_board()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
    
    def change_difficulty(self, difficulty: Difficulty):
        """Change game difficulty"""
        self.current_difficulty = difficulty
        self.game.reset(difficulty)
        self.start_time = None
        self.elapsed_time = 0
        
        # Recalculate window size
        self.board_width = self.game.cols * self.cell_size
        self.board_height = self.game.rows * self.cell_size
        self.window_width = self.board_width + 2 * self.border_width
        self.window_height = self.board_height + self.header_height + 2 * self.border_width
        
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        
        # Reposition smiley
        self.smiley_rect = pygame.Rect(
            self.window_width // 2 - 25,
            20,
            50,
            50
        )
    
    def run_with_ai(self, agent, delay_ms=200, auto_restart=False, max_games=1):
        """
        Run the game with an AI agent playing
        
        Args:
            agent: AI agent instance
            delay_ms: Delay between moves in milliseconds
            auto_restart: Whether to automatically restart after game ends
            max_games: Maximum number of games to play (0 = infinite)
        """
        games_played = 0
        games_won = 0
        games_lost = 0
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Pause/unpause
                        print("Paused. Press SPACE to continue, ESC to quit.")
                        paused = True
                        while paused:
                            for e in pygame.event.get():
                                if e.type == pygame.QUIT:
                                    self.running = False
                                    paused = False
                                elif e.type == pygame.KEYDOWN:
                                    if e.key == pygame.K_SPACE:
                                        paused = False
                                    elif e.key == pygame.K_ESCAPE:
                                        self.running = False
                                        paused = False
                    elif event.key == pygame.K_r:
                        # Manual restart
                        self.game.reset(self.current_difficulty)
                        self.start_time = None
                        self.elapsed_time = 0
                        agent.game = self.game
            
            # Draw current state
            self.screen.fill(COLORS['bg'])
            self.draw_header()
            self.draw_board()
            
            # Draw AI info
            stats = agent.calculate_statistics()
            info_text = f"Games: {games_played} | Won: {games_won} | Lost: {games_lost} | Progress: {stats['progress']:.1f}%"
            text_surface = self.font_small.render(info_text, True, COLORS['text'])
            self.screen.blit(text_surface, (10, self.window_height - 25))
            
            controls_text = "SPACE: Pause | R: Restart | ESC: Quit"
            controls_surface = self.font_small.render(controls_text, True, COLORS['text'])
            self.screen.blit(controls_surface, (10, self.window_height - 50))
            
            pygame.display.flip()
            
            # AI makes a move
            if self.game.game_state == GameState.PLAYING or self.game.game_state == GameState.READY:
                action = agent.choose_action()
                
                if action:
                    action_type, row, col = action
                    
                    if action_type == 'reveal':
                        self.game.reveal_cell(row, col)
                    elif action_type == 'flag':
                        self.game.toggle_flag(row, col)
                    
                    # Wait before next move
                    pygame.time.delay(delay_ms)
                else:
                    # No valid action, game might be stuck
                    print("Agent has no valid moves!")
                    pygame.time.delay(2000)
                    if auto_restart:
                        self.game.reset(self.current_difficulty)
                        self.start_time = None
                        self.elapsed_time = 0
                        agent.game = self.game
            
            elif self.game.game_state in [GameState.WON, GameState.LOST]:
                # Game ended
                games_played += 1
                if self.game.game_state == GameState.WON:
                    games_won += 1
                    print(f"🎉 AI WON game #{games_played}! Time: {self.elapsed_time}s")
                else:
                    games_lost += 1
                    print(f"💥 AI LOST game #{games_played}")
                
                # Show result for a moment
                pygame.time.delay(2000)
                
                # Check if we should continue
                if max_games > 0 and games_played >= max_games:
                    print(f"\nCompleted {games_played} games!")
                    print(f"Win rate: {games_won/games_played*100:.1f}%")
                    self.running = False
                elif auto_restart:
                    self.game.reset(self.current_difficulty)
                    self.start_time = None
                    self.elapsed_time = 0
                    agent.game = self.game
                else:
                    # Wait for user to restart or quit
                    waiting = True
                    while waiting and self.running:
                        for e in pygame.event.get():
                            if e.type == pygame.QUIT:
                                self.running = False
                                waiting = False
                            elif e.type == pygame.KEYDOWN:
                                if e.key == pygame.K_r:
                                    self.game.reset(self.current_difficulty)
                                    self.start_time = None
                                    self.elapsed_time = 0
                                    agent.game = self.game
                                    waiting = False
            
            self.clock.tick(60)
        
        pygame.quit()
        
        # Print final statistics
        if games_played > 0:
            print("\n" + "="*50)
            print("FINAL STATISTICS")
            print("="*50)
            print(f"Games played: {games_played}")
            print(f"Games won: {games_won}")
            print(f"Games lost: {games_lost}")
            print(f"Win rate: {games_won/games_played*100:.1f}%")
            print("="*50)