import pygame
import random 

def snake_game():
    # Initialize pygame
    pygame.init()

    # Set display dimensions
    WIDTH, HEIGHT = 600, 400
    BLOCK_SIZE = 20
    FPS = 15

    # Define colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (213, 50, 80)
    GREEN = (0, 255, 0)
    BLUE = (50, 153, 213)

    # Set up the display
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake v3.3")

    # Clock for controlling the game's FPS
    clock = pygame.time.Clock()

    # Define fonts
    font_style = pygame.font.SysFont(None, 30)

    # Function to display message on screen
    def message(msg, color):
        mesg = font_style.render(msg, True, color)
        screen.blit(mesg, [WIDTH / 6, HEIGHT / 3])

    # Function to draw the snake
    def draw_snake(snake_block, snake_list):
        for x in snake_list:
            pygame.draw.rect(screen, GREEN, [x[0], x[1], snake_block, snake_block])

    # Function to display score
    def display_score(score):
        score_text = font_style.render("Score: " + str(score), True, BLACK)
        screen.blit(score_text, [10, 10])

    # Main game loop
    game_over = False
    game_close = False

    # Initial position of the snake
    x1 = WIDTH / 2
    y1 = HEIGHT / 2
    x1_change = 0
    y1_change = 0

    # Length of the snake
    snake_list = []
    length_of_snake = 1

    # Initial position of the food
    food_x = round(random.randrange(0, WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
    food_y = round(random.randrange(0, HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE

    # Initial score
    score = 0

    while not game_over:
        screen.fill(BLUE)  # Fill the screen with the background color

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -BLOCK_SIZE
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = BLOCK_SIZE
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -BLOCK_SIZE
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = BLOCK_SIZE
                    x1_change = 0

        # Check if snake hits the boundary
        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0:
            game_close = True
        x1 += x1_change
        y1 += y1_change

        # Draw the food
        pygame.draw.rect(screen, RED, [food_x, food_y, BLOCK_SIZE, BLOCK_SIZE])

        # Draw the snake
        snake_head = []
        snake_head.append(x1)
        snake_head.append(y1)
        snake_list.append(snake_head)
        if len(snake_list) > length_of_snake:
            del snake_list[0]

        # Check if snake collides with itself
        for x in snake_list[:-1]:
            if x == snake_head:
                game_close = True

        draw_snake(BLOCK_SIZE, snake_list)

        # Update and display score
        display_score(score)

        # Check if snake eats food
        if x1 == food_x and y1 == food_y:
            food_x = round(random.randrange(0, WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
            food_y = round(random.randrange(0, HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
            length_of_snake += 1
            score += 1

        # Control the frame rate
        clock.tick(FPS)

        # Check game over condition
        while game_close:
            screen.fill(BLUE)
            message("You lost! Press Q to Quit or R to Play Again", RED)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_r:
                        snake_game()

        pygame.display.update()  

    pygame.quit()
if __name__ == "__main__":
    snake_game()