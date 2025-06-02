import pygame
import random
import sys

pygame.init()

# Constants
CELL_SIZE = 30
GRID_SIZE = 9  # 9x9 grid
MINES_COUNT = 10
WIDTH, HEIGHT = CELL_SIZE * GRID_SIZE, CELL_SIZE * GRID_SIZE + 40  # extra space for messages

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (160, 160, 160)
DARK_GRAY = (100, 100, 100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minesweeper (build 27)")

font = pygame.font.SysFont(None, 24)

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.adjacent_mines = 0

def create_grid():
    grid = [[Cell(x, y) for x in range(GRID_SIZE)] for y in range(GRID_SIZE)]
    return grid

def place_mines(grid, first_click_pos):
    # Avoid placing a mine on the first clicked cell or adjacent to it
    safe_cells = []
    fx, fy = first_click_pos
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if abs(x - fx) <= 1 and abs(y - fy) <= 1:
                continue
            safe_cells.append((x, y))
    mines = random.sample(safe_cells, MINES_COUNT)
    for (x, y) in mines:
        grid[y][x].is_mine = True

def count_adjacent_mines(grid):
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            if grid[y][x].is_mine:
                continue
            count = 0
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                        if grid[ny][nx].is_mine:
                            count += 1
            grid[y][x].adjacent_mines = count

def reveal_cell(grid, x, y):
    cell = grid[y][x]
    if cell.is_revealed or cell.is_flagged:
        return
    cell.is_revealed = True
    # If no adjacent mines, reveal neighbors recursively
    if cell.adjacent_mines == 0 and not cell.is_mine:
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    if not grid[ny][nx].is_revealed:
                        reveal_cell(grid, nx, ny)

def check_win(grid):
    for row in grid:
        for cell in row:
            if not cell.is_mine and not cell.is_revealed:
                return False
    return True

def draw_grid(grid):
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            cell = grid[y][x]
            rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if cell.is_revealed:
                pygame.draw.rect(screen, GRAY, rect)
                if cell.is_mine:
                    pygame.draw.circle(screen, BLACK, rect.center, CELL_SIZE // 3)
                elif cell.adjacent_mines > 0:
                    text = font.render(str(cell.adjacent_mines), True, BLUE)
                    text_rect = text.get_rect(center=rect.center)
                    screen.blit(text, text_rect)
            else:
                pygame.draw.rect(screen, DARK_GRAY, rect)
                if cell.is_flagged:
                    pygame.draw.circle(screen, RED, rect.center, CELL_SIZE // 3)
            pygame.draw.rect(screen, BLACK, rect, 1)

def main():
    grid = create_grid()
    first_click = True
    game_over = False
    won = False

    while True:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if not game_over:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    # Only handle clicks inside the grid area
                    if my < CELL_SIZE * GRID_SIZE:
                        x, y = mx // CELL_SIZE, my // CELL_SIZE
                        if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                            cell = grid[y][x]
                            if event.button == 1:  # Left click to reveal
                                if first_click:
                                    place_mines(grid, (x, y))
                                    count_adjacent_mines(grid)
                                    first_click = False
                                if not cell.is_flagged:
                                    reveal_cell(grid, x, y)
                                    if cell.is_mine:
                                        game_over = True
                                    elif check_win(grid):
                                        won = True
                                        game_over = True
                            elif event.button == 3:  # Right click to flag
                                if not cell.is_revealed:
                                    cell.is_flagged = not cell.is_flagged

        draw_grid(grid)

        # Draw messages
        msg = ""
        if game_over:
            msg = "You Win!" if won else "Game Over!"
        else:
            msg = "Left click to reveal, Right click to flag"

        text = font.render(msg, True, BLACK)
        screen.blit(text, (10, HEIGHT - 30))

        pygame.display.flip()

main()

