# Copyright 2025 the FranchukOS project authors. 
# Contributed under the Apache License, Version 2.0.

import pygame
import random

# Initialize pygame
pygame.init()

# Screen dimensions
CELL_SIZE = 30
COLS, ROWS = 10, 20
WIDTH, HEIGHT = CELL_SIZE * COLS, CELL_SIZE * ROWS

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris (build 23)")

# Colors
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255),  # I
    (0, 0, 255),    # J
    (255, 165, 0),  # L
    (255, 255, 0),  # O
    (0, 255, 0),    # S
    (128, 0, 128),  # T
    (255, 0, 0),    # Z
]

# Tetromino shapes in 4x4 grids (each string represents a row)
SHAPES = [
    ['..X.',
     '..X.',
     '..X.',
     '..X.'],  # I

    ['.X..',
     '.X..',
     'XX..',
     '....'],  # J

    ['..X.',
     '..X.',
     '.XX.',
     '....'],  # L

    ['.XX.',
     '.XX.',
     '....',
     '....'],  # O

    ['..XX',
     '.XX.',
     '....',
     '....'],  # S

    ['.X..',
     'XXX.',
     '....',
     '....'],  # T

    ['.XX.',
     '..XX',
     '....',
     '....'],  # Z
]

class Piece:
    def __init__(self, x, y, shape_idx):
        self.x = x
        self.y = y
        self.shape_idx = shape_idx
        self.shape = SHAPES[shape_idx]
        self.color = COLORS[shape_idx]
        self.rotation = 0  # 0-3

    def image(self):
        return self.rotate(self.shape, self.rotation)

    @staticmethod
    def rotate(shape, rotation):
        grid = [list(row) for row in shape]
        for _ in range(rotation % 4):
            grid = list(zip(*grid[::-1]))  # rotate 90 degrees
        return [''.join(row) for row in grid]

def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
    for (x, y), color in locked_positions.items():
        if y > -1:
            grid[y][x] = color
    return grid

def convert_shape_format(piece):
    positions = []
    shape = piece.image()
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell == 'X':
                x = piece.x + j
                y = piece.y + i
                positions.append((x, y))
    return positions

def valid_space(piece, grid):
    formatted = convert_shape_format(piece)
    for x, y in formatted:
        if x < 0 or x >= COLS or y >= ROWS:
            return False
        if y >= 0 and grid[y][x] != BLACK:
            return False
    return True

def check_lost(positions):
    for (x, y) in positions:
        if y < 1:
            return True
    return False

def clear_rows(grid, locked):
    cleared = 0
    for i in range(len(grid)-1, -1, -1):
        if BLACK not in grid[i]:
            cleared += 1
            # Remove locked positions in that row
            for j in range(COLS):
                try:
                    del locked[(j, i)]
                except:
                    pass
            # Move every other row down
            for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
                x, y = key
                if y < i:
                    locked[(x, y + 1)] = locked.pop(key)
    return cleared

def draw_grid(surface, grid):
    for i in range(ROWS):
        for j in range(COLS):
            pygame.draw.rect(surface, grid[i][j], (j*CELL_SIZE, i*CELL_SIZE, CELL_SIZE, CELL_SIZE), 0)
            pygame.draw.rect(surface, GRAY, (j*CELL_SIZE, i*CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

def draw_window(surface, grid, score=0):
    surface.fill(BLACK)
    draw_grid(surface, grid)
    # Draw score
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render(f'Score: {score}', True, (255, 255, 255))
    surface.blit(label, (10, 10))

def main():
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = Piece(3, 0, random.randint(0, len(SHAPES) - 1))
    next_piece = Piece(3, 0, random.randint(0, len(SHAPES) - 1))
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5
    score = 0

    while run:
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotation = (current_piece.rotation + 1) % 4
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation - 1) % 4

        shape_pos = convert_shape_format(current_piece)

        for pos in shape_pos:
            x, y = pos
            if 0 <= x < COLS and 0 <= y < ROWS:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                x, y = pos
                if 0 <= x < COLS and 0 <= y < ROWS:
                    locked_positions[(x, y)] = current_piece.color
            current_piece = next_piece
            next_piece = Piece(3, 0, random.randint(0, len(SHAPES) - 1))
            change_piece = False

            cleared = clear_rows(grid, locked_positions)
            if cleared > 0:
                score += cleared * 10

            grid = create_grid(locked_positions)

        draw_window(screen, grid, score)
        pygame.display.update()

        if check_lost(locked_positions):
            run = False

    pygame.quit()