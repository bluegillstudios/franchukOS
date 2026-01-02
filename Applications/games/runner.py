import pygame
import random
import sys

# -------------------- SETUP --------------------
pygame.init()
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Endless Runner - Achievements")

clock = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 36)
ACHIEVE_FONT = pygame.font.SysFont(None, 28)

# -------------------- COLORS --------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 60, 60)
BLUE = (60, 120, 220)
GREEN = (80, 200, 120)
SKY = (150, 200, 255)
MOUNTAIN = (100, 120, 150)
CLOUD = (220, 220, 220)
YELLOW = (240, 220, 60)

# -------------------- PLAYER --------------------
player_size = 40
player_x = 100
player_y = HEIGHT - player_size - 40
player_vel_y = 0
gravity = 1
jump_power = -16
jump_count = 0
max_jumps = 2
total_jumps = 0

# -------------------- GROUND --------------------
ground_y = HEIGHT - 40

# -------------------- OBSTACLES --------------------
obstacles = []
obstacle_timer = 0
obstacle_delay = 1300
game_speed = 7
obstacles_dodged = 0

# -------------------- BACKGROUND --------------------
bg_scroll = 0
bg_speed = 2
clouds = [(random.randint(0, WIDTH), random.randint(50, 150)) for _ in range(8)]
mountains = [(i * 200, HEIGHT - 150 - random.randint(0, 50)) for i in range(5)]

# -------------------- SCORE --------------------
score = 0
start_ticks = pygame.time.get_ticks()

# -------------------- ACHIEVEMENTS --------------------
achievements = {
    "Where we going?": False,
    "Fingers of wood": False,
    "Fingers of steel": False,
    "Don't stop me now": False,
    "To infinity and beyond": False,
    "Need a drink?": False,
    "Well I'll be!": False,
    "For the memes": False,
    "Did it for big T": False,
    "Like a bunny": False,
    "Could've jumped to space": False,
    "Even better than a bunny": False,
    "Hippity hoppity": False,
    "Reaction time": False,
    "Got it to a tee": False,
    "Way to be": False,
    "Just a pro": False,
    "How?": False
}
achievement_messages = []

def unlock_achievement(name):
    if not achievements[name]:
        achievements[name] = True
        achievement_messages.append([name, 180])
        print(f"Achievement unlocked: {name}")

# -------------------- FUNCTIONS --------------------
def draw_player():
    pygame.draw.rect(screen, BLUE, (player_x, player_y, player_size, player_size))

def draw_ground():
    pygame.draw.rect(screen, GREEN, (0, ground_y, WIDTH, 40))

def spawn_obstacle():
    height = random.randint(30, 60)
    width = random.randint(20, 40)
    x = WIDTH + random.randint(0, 100)
    y = ground_y - height
    obstacles.append({
        "rect": pygame.Rect(x, y, width, height),
        "counted": False
    })

def move_obstacles():
    global obstacles, obstacles_dodged
    for obs in obstacles:
        obs["rect"].x -= game_speed

        if obs["rect"].right < player_x and not obs["counted"]:
            obstacles_dodged += 1
            obs["counted"] = True

    obstacles = [o for o in obstacles if o["rect"].right > 0]

def draw_obstacles():
    for obs in obstacles:
        pygame.draw.rect(screen, RED, obs["rect"])

def check_collision():
    player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
    for obs in obstacles:
        if player_rect.colliderect(obs["rect"]):
            return True
    return False

def draw_score():
    screen.blit(FONT.render(f"Score: {score}", True, BLACK), (10, 10))

def draw_background():
    global bg_scroll
    screen.fill(SKY)

    for mx, my in mountains:
        pygame.draw.polygon(
            screen, MOUNTAIN,
            [(mx - bg_scroll * 0.5, my),
             (mx + 100 - bg_scroll * 0.5, my + 100),
             (mx - 200 - bg_scroll * 0.5, my + 100)]
        )

    for cx, cy in clouds:
        pygame.draw.ellipse(screen, CLOUD, (cx - bg_scroll * 1.2, cy, 80, 40))

    bg_scroll += bg_speed
    if bg_scroll > WIDTH:
        bg_scroll = 0

def draw_achievements():
    y = 50
    for msg, timer in achievement_messages:
        txt = ACHIEVE_FONT.render(f"Achievement Unlocked: {msg}", True, YELLOW)
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, y))
        y += 30
    for m in achievement_messages:
        m[1] -= 1
    achievement_messages[:] = [m for m in achievement_messages if m[1] > 0]

def game_over():
    txt = FONT.render("GAME OVER - Press R to Restart", True, BLACK)
    screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                return

# -------------------- MAIN LOOP --------------------
running = True
while running:
    clock.tick(60)
    draw_background()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and jump_count < max_jumps:
                player_vel_y = jump_power
                jump_count += 1
                total_jumps += 1

    # Physics
    player_vel_y += gravity
    player_y += player_vel_y

    if player_y >= ground_y - player_size:
        player_y = ground_y - player_size
        player_vel_y = 0
        jump_count = 0

    # Obstacles
    obstacle_timer += clock.get_time()
    if obstacle_timer > obstacle_delay:
        spawn_obstacle()
        obstacle_timer = 0

    move_obstacles()

    # Difficulty
    score = (pygame.time.get_ticks() - start_ticks) // 100
    game_speed = 7 + score // 15
    bg_speed = 2 + score // 80
    obstacle_delay = max(700, 1300 - score // 2)

    # ACHIEVEMENTS
    if score >= 500: unlock_achievement("Where we going?")
    if score >= 1000: unlock_achievement("Fingers of wood")
    if score >= 5000: unlock_achievement("Fingers of steel")
    if score >= 10000: unlock_achievement("Don't stop me now")
    if score >= 50000: unlock_achievement("To infinity and beyond")
    if score >= 100000: unlock_achievement("Need a drink?")
    if score >= 500000: unlock_achievement("Well I'll be!")
    if score >= 1000000: unlock_achievement("For the memes")
    if score >= 10000000: unlock_achievement("Did it for big T")

    if total_jumps >= 20: unlock_achievement("Like a bunny")
    if total_jumps >= 200: unlock_achievement("Could've jumped to space")
    if total_jumps >= 1000:
        unlock_achievement("Even better than a bunny")
    if total_jumps >= 5000:
        unlock_achievement("Hippity hoppity")

    if obstacles_dodged >= 10: unlock_achievement("Reaction time")
    if obstacles_dodged >= 25: unlock_achievement("Got it to a tee")
    if obstacles_dodged >= 100: unlock_achievement("Way to be")
    if obstacles_dodged >= 1000: unlock_achievement("Just a pro")
    if obstacles_dodged >= 10000: unlock_achievement("How?")

    # Draw
    draw_ground()
    draw_player()
    draw_obstacles()
    draw_score()
    draw_achievements()

    if check_collision():
        game_over()
        obstacles.clear()
        achievement_messages.clear()
        total_jumps = obstacles_dodged = 0
        player_y = ground_y - player_size
        player_vel_y = 0
        start_ticks = pygame.time.get_ticks()

    pygame.display.flip()
