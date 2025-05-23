import pygame
import random
import sys
import time
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
MAZE_WIDTH = 800
MAZE_HEIGHT = 600
MENU_WIDTH = 200

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 200)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)


class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3
    PAUSE = 4
    CREDITS = 5


class Difficulty:
    EASY = {"size": 15, "name": "Easy"}
    MEDIUM = {"size": 25, "name": "Medium"}
    HARD = {"size": 35, "name": "Hard"}


class MazeGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.maze = [[1 for _ in range(width)] for _ in range(height)]

    def generate_maze(self):
        """Generate maze using DFS algorithm"""
        # Start from (1,1)
        start_x, start_y = 1, 1
        self.maze[start_y][start_x] = 0

        stack = [(start_x, start_y)]

        while stack:
            current_x, current_y = stack[-1]
            neighbors = self.get_unvisited_neighbors(current_x, current_y)

            if neighbors:
                next_x, next_y = random.choice(neighbors)
                # Remove the wall between current and next cell
                wall_x = (current_x + next_x) // 2
                wall_y = (current_y + next_y) // 2
                self.maze[wall_y][wall_x] = 0
                self.maze[next_y][next_x] = 0
                stack.append((next_x, next_y))
            else:
                stack.pop()

        # Ensure start and end are open
        self.maze[1][1] = 0  # Start
        self.maze[self.height - 2][self.width - 2] = 0  # End

        return self.maze

    def get_unvisited_neighbors(self, x, y):
        neighbors = []
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (1 <= nx < self.width - 1 and 1 <= ny < self.height - 1 and
                    self.maze[ny][nx] == 1):
                neighbors.append((nx, ny))

        return neighbors


class Player:
    def __init__(self, x, y, cell_size):
        self.x = x
        self.y = y
        self.cell_size = cell_size
        self.pixel_x = x * cell_size
        self.pixel_y = y * cell_size

    def move(self, dx, dy, maze):
        new_x = self.x + dx
        new_y = self.y + dy

        if (0 <= new_x < len(maze[0]) and 0 <= new_y < len(maze) and
                maze[new_y][new_x] == 0):
            self.x = new_x
            self.y = new_y
            self.pixel_x = self.x * self.cell_size
            self.pixel_y = self.y * self.cell_size
            return True
        return False

    def draw(self, screen, offset_x, offset_y):
        pygame.draw.circle(screen, BLUE,
                           (self.pixel_x + self.cell_size // 2 + offset_x,
                            self.pixel_y + self.cell_size // 2 + offset_y),
                           self.cell_size // 3)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Maze Escape - Labyrinth Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)

        self.state = GameState.MENU
        self.difficulty = Difficulty.EASY
        self.maze = None
        self.player = None
        self.start_time = 0
        self.end_time = 0
        self.score = 0
        self.moves = 0

        # Credits scroll offset
        self.credits_scroll = 0
        self.credits_speed = 1

    def generate_new_maze(self):
        """Generate a new maze based on current difficulty"""
        size = self.difficulty["size"]
        generator = MazeGenerator(size, size)
        self.maze = generator.generate_maze()

        # Calculate cell size to fit in the maze area
        self.cell_size = min(MAZE_WIDTH // size, MAZE_HEIGHT // size)

        # Create player at start position
        self.player = Player(1, 1, self.cell_size)

        # Reset game stats
        self.start_time = time.time()
        self.moves = 0
        self.score = 0

    def draw_maze(self):
        """Draw the maze on screen"""
        if not self.maze:
            return

        maze_offset_x = 10
        maze_offset_y = (WINDOW_HEIGHT - len(self.maze) * self.cell_size) // 2

        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                rect = pygame.Rect(x * self.cell_size + maze_offset_x,
                                   y * self.cell_size + maze_offset_y,
                                   self.cell_size, self.cell_size)

                if cell == 1:  # Wall
                    pygame.draw.rect(self.screen, BLACK, rect)
                else:  # Path
                    pygame.draw.rect(self.screen, WHITE, rect)

                pygame.draw.rect(self.screen, GRAY, rect, 1)

        # Draw start (green) and end (red) positions
        start_rect = pygame.Rect(1 * self.cell_size + maze_offset_x,
                                 1 * self.cell_size + maze_offset_y,
                                 self.cell_size, self.cell_size)
        pygame.draw.rect(self.screen, GREEN, start_rect)

        end_x, end_y = len(self.maze[0]) - 2, len(self.maze) - 2
        end_rect = pygame.Rect(end_x * self.cell_size + maze_offset_x,
                               end_y * self.cell_size + maze_offset_y,
                               self.cell_size, self.cell_size)
        pygame.draw.rect(self.screen, RED, end_rect)

        # Draw player
        if self.player:
            self.player.draw(self.screen, maze_offset_x, maze_offset_y)

    def draw_ui(self):
        """Draw game UI elements"""
        # Background for UI area
        ui_rect = pygame.Rect(MAZE_WIDTH + 20, 0, MENU_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, LIGHT_GRAY, ui_rect)
        pygame.draw.rect(self.screen, BLACK, ui_rect, 2)

        y_offset = 50

        # Difficulty
        diff_text = self.font.render("Difficulty:", True, BLACK)
        self.screen.blit(diff_text, (MAZE_WIDTH + 30, y_offset))
        diff_name = self.small_font.render(self.difficulty["name"], True, BLUE)
        self.screen.blit(diff_name, (MAZE_WIDTH + 30, y_offset + 30))

        y_offset += 80

        # Timer
        if self.state == GameState.PLAYING:
            elapsed = int(time.time() - self.start_time)
        else:
            elapsed = int(self.end_time - self.start_time) if self.end_time else 0

        timer_text = self.font.render("Time:", True, BLACK)
        self.screen.blit(timer_text, (MAZE_WIDTH + 30, y_offset))
        time_value = self.small_font.render(f"{elapsed}s", True, BLUE)
        self.screen.blit(time_value, (MAZE_WIDTH + 30, y_offset + 30))

        y_offset += 80

        # Moves
        moves_text = self.font.render("Moves:", True, BLACK)
        self.screen.blit(moves_text, (MAZE_WIDTH + 30, y_offset))
        moves_value = self.small_font.render(str(self.moves), True, BLUE)
        self.screen.blit(moves_value, (MAZE_WIDTH + 30, y_offset + 30))

        y_offset += 80

        # Score
        score_text = self.font.render("Score:", True, BLACK)
        self.screen.blit(score_text, (MAZE_WIDTH + 30, y_offset))
        score_value = self.small_font.render(str(self.score), True, BLUE)
        self.screen.blit(score_value, (MAZE_WIDTH + 30, y_offset + 30))

        y_offset += 100

        # Controls
        controls_text = self.small_font.render("Controls:", True, BLACK)
        self.screen.blit(controls_text, (MAZE_WIDTH + 30, y_offset))

        controls = ["Arrow Keys - Move", "R - Restart", "ESC - Menu"]
        for i, control in enumerate(controls):
            control_text = self.small_font.render(control, True, DARK_GRAY)
            self.screen.blit(control_text, (MAZE_WIDTH + 30, y_offset + 30 + i * 25))

    def draw_menu(self):
        """Draw main menu"""
        self.screen.fill(WHITE)

        # Title
        title = self.large_font.render("MAZE ESCAPE", True, BLACK)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 120))
        self.screen.blit(title, title_rect)

        subtitle = self.small_font.render("Labyrinth Game with Python", True, GRAY)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 155))
        self.screen.blit(subtitle, subtitle_rect)

        # Difficulty selection
        diff_title = self.font.render("Select Difficulty:", True, BLACK)
        diff_rect = diff_title.get_rect(center=(WINDOW_WIDTH // 2, 220))
        self.screen.blit(diff_title, diff_rect)

        difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]
        colors = [GREEN, ORANGE, RED]  # Changed YELLOW to ORANGE for better visibility

        for i, (diff, color) in enumerate(zip(difficulties, colors)):
            y_pos = 270 + i * 50

            # Highlight current difficulty
            if diff == self.difficulty:
                highlight_rect = pygame.Rect(WINDOW_WIDTH // 2 - 120, y_pos - 5, 240, 35)
                pygame.draw.rect(self.screen, LIGHT_GRAY, highlight_rect)

            diff_text = self.font.render(f"{i + 1}. {diff['name']} ({diff['size']}x{diff['size']})",
                                         True, color)
            diff_rect = diff_text.get_rect(center=(WINDOW_WIDTH // 2, y_pos + 10))
            self.screen.blit(diff_text, diff_rect)

        # Menu options
        menu_options = [
            ("Press SPACE to start game", WHITE),
            ("Press C for Credits", PURPLE)
        ]

        for i, (option, color) in enumerate(menu_options):
            option_text = self.font.render(option, True, color)
            option_rect = option_text.get_rect(center=(WINDOW_WIDTH // 2, 440 + i * 40))

            # Add background for better visibility
            bg_rect = pygame.Rect(option_rect.x - 10, option_rect.y - 5,
                                  option_rect.width + 20, option_rect.height + 10)
            pygame.draw.rect(self.screen, BLACK, bg_rect)
            self.screen.blit(option_text, option_rect)

        # Instructions
        instructions = [
            "Use arrow keys to navigate the maze",
            "Reach the red square to win!"
        ]

        for i, instruction in enumerate(instructions):
            inst_text = self.small_font.render(instruction, True, DARK_GRAY)
            inst_rect = inst_text.get_rect(center=(WINDOW_WIDTH // 2, 550 + i * 25))
            self.screen.blit(inst_text, inst_rect)

    def draw_credits(self):
        """Draw credits screen with scrolling animation"""
        self.screen.fill(BLACK)

        # Credits data
        credits_data = [
            {"text": "MAZE ESCAPE", "font": self.large_font, "color": YELLOW, "spacing": 80},
            {"text": "Development Team", "font": self.font, "color": WHITE, "spacing": 60},

            {"text": "Mert Kaymak", "font": self.font, "color": BLUE, "spacing": 40},
            {"text": "Game Logic & Pathfinding Algorithm", "font": self.small_font, "color": LIGHT_GRAY, "spacing": 50},

            {"text": "Ahmet Alperen Arslan", "font": self.font, "color": GREEN, "spacing": 40},
            {"text": "Graphical Interface (GUI) & Visual Design", "font": self.small_font, "color": LIGHT_GRAY,
             "spacing": 50},

            {"text": "Yalçın Kağan Çakır", "font": self.font, "color": RED, "spacing": 40},
            {"text": "Data Structures, Collision Mechanics & Level Design", "font": self.small_font,
             "color": LIGHT_GRAY, "spacing": 50},

            {"text": "Utkan Onur Özbedel", "font": self.font, "color": ORANGE, "spacing": 40},
            {"text": "Testing, Bug Fixing & Documentation", "font": self.small_font, "color": LIGHT_GRAY,
             "spacing": 60},

            {"text": "Special Thanks", "font": self.font, "color": WHITE, "spacing": 50},
            {"text": "Built with Python & Pygame", "font": self.small_font, "color": PURPLE, "spacing": 40},
            {"text": "© 2025 Powerpuff Girls Team", "font": self.small_font, "color": GRAY, "spacing": 80},

            {"text": "Thank you for playing!", "font": self.font, "color": YELLOW, "spacing": 60},
        ]

        # Calculate total height of credits
        total_height = sum(item["spacing"] for item in credits_data)

        # Draw credits with scroll offset
        current_y = WINDOW_HEIGHT - self.credits_scroll

        for item in credits_data:
            if -50 < current_y < WINDOW_HEIGHT + 50:  # Only draw visible text
                text_surface = item["font"].render(item["text"], True, item["color"])
                text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, current_y))
                self.screen.blit(text_surface, text_rect)

            current_y += item["spacing"]

        # Update scroll position
        self.credits_scroll += self.credits_speed

        # Reset scroll when credits finish
        if self.credits_scroll > total_height + WINDOW_HEIGHT:
            self.credits_scroll = 0

        # Instructions at bottom
        instruction = "Press ESC to return to menu"
        inst_surface = self.small_font.render(instruction, True, WHITE)
        inst_rect = inst_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))

        # Add background for better visibility
        bg_rect = pygame.Rect(inst_rect.x - 10, inst_rect.y - 5,
                              inst_rect.width + 20, inst_rect.height + 10)
        pygame.draw.rect(self.screen, DARK_GRAY, bg_rect)
        self.screen.blit(inst_surface, inst_rect)

    def draw_game_over(self):
        """Draw game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Game Over text
        game_over_text = self.font.render("MAZE COMPLETED!", True, WHITE)
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, 200))
        self.screen.blit(game_over_text, game_over_rect)

        # Stats
        elapsed = int(self.end_time - self.start_time)
        stats = [
            f"Time: {elapsed} seconds",
            f"Moves: {self.moves}",
            f"Score: {self.score}",
            f"Difficulty: {self.difficulty['name']}"
        ]

        for i, stat in enumerate(stats):
            stat_text = self.small_font.render(stat, True, WHITE)
            stat_rect = stat_text.get_rect(center=(WINDOW_WIDTH // 2, 260 + i * 30))
            self.screen.blit(stat_text, stat_rect)

        # Options
        options = [
            "Press R to play again",
            "Press ESC to return to menu"
        ]

        for i, option in enumerate(options):
            option_text = self.small_font.render(option, True, YELLOW)
            option_rect = option_text.get_rect(center=(WINDOW_WIDTH // 2, 400 + i * 30))
            self.screen.blit(option_text, option_rect)

    def calculate_score(self):
        """Calculate player score based on time and moves"""
        if self.end_time and self.start_time:
            elapsed = self.end_time - self.start_time
            base_score = 1000
            time_penalty = int(elapsed * 2)
            move_penalty = self.moves * 5
            difficulty_bonus = {"Easy": 0, "Medium": 500, "Hard": 1000}[self.difficulty["name"]]

            self.score = max(0, base_score - time_penalty - move_penalty + difficulty_bonus)

    def check_win_condition(self):
        """Check if player reached the end"""
        if self.player and self.maze:
            end_x, end_y = len(self.maze[0]) - 2, len(self.maze) - 2
            if self.player.x == end_x and self.player.y == end_y:
                self.end_time = time.time()
                self.calculate_score()
                self.state = GameState.GAME_OVER
                return True
        return False

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_1:
                        self.difficulty = Difficulty.EASY
                    elif event.key == pygame.K_2:
                        self.difficulty = Difficulty.MEDIUM
                    elif event.key == pygame.K_3:
                        self.difficulty = Difficulty.HARD
                    elif event.key == pygame.K_SPACE:
                        self.generate_new_maze()
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_c:
                        self.state = GameState.CREDITS
                        self.credits_scroll = 0  # Reset scroll position

                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_UP:
                        if self.player.move(0, -1, self.maze):
                            self.moves += 1
                    elif event.key == pygame.K_DOWN:
                        if self.player.move(0, 1, self.maze):
                            self.moves += 1
                    elif event.key == pygame.K_LEFT:
                        if self.player.move(-1, 0, self.maze):
                            self.moves += 1
                    elif event.key == pygame.K_RIGHT:
                        if self.player.move(1, 0, self.maze):
                            self.moves += 1
                    elif event.key == pygame.K_r:
                        self.generate_new_maze()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU

                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        self.generate_new_maze()
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU

                elif self.state == GameState.CREDITS:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU

        return True

    def update(self):
        """Update game state"""
        if self.state == GameState.PLAYING:
            self.check_win_condition()

    def draw(self):
        """Draw everything"""
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.screen.fill(WHITE)
            self.draw_maze()
            self.draw_ui()
        elif self.state == GameState.GAME_OVER:
            self.screen.fill(WHITE)
            self.draw_maze()
            self.draw_ui()
            self.draw_game_over()
        elif self.state == GameState.CREDITS:
            self.draw_credits()

    def run(self):
        """Main game loop"""
        running = True

        while running:
            running = self.handle_events()
            self.update()
            self.draw()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


# Main execution
if __name__ == "__main__":
    game = Game()
    game.run()