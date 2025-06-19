import pygame
import math
import random

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Raycast FPS")
clock = pygame.time.Clock()

# Sounds
shoot_sound = pygame.mixer.Sound("shoot.wav")
hit_sound = pygame.mixer.Sound("hit.wav")

FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = 120
MAX_DEPTH = 800
DELTA_ANGLE = FOV / NUM_RAYS
DIST = NUM_RAYS / (2 * math.tan(HALF_FOV))
PROJ_COEFF = 3 * DIST * TILE_SIZE
SCALE = WIDTH // NUM_RAYS

TILE_SIZE = 64
MAP_WIDTH, MAP_HEIGHT = 10, 10

game_map = [
    [1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,1,0,0,0,1,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,1,0,1,0,1,0,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,1,1,0,1],
    [1,1,1,1,1,1,1,1,1,1],
]

game_state = 'menu'
menu_options = ["Play", "Quit"]
pause_options = ["Resume", "Quit"]
gameover_options = ["Restart", "Quit"]
selected_option = 0
running = True

class Player:
    def __init__(self):
        self.x, self.y = TILE_SIZE * 3, TILE_SIZE * 3
        self.angle = 0
        self.health = 100
        self.ammo = 10
        self.reload_time = 0
        self.score = 0

    def movement(self, keys):
        speed = 3
        if keys[pygame.K_w]:
            dx = math.cos(self.angle) * speed
            dy = math.sin(self.angle) * speed
            if not wall_at(self.x + dx, self.y): self.x += dx
            if not wall_at(self.x, self.y + dy): self.y += dy
        if keys[pygame.K_s]:
            dx = -math.cos(self.angle) * speed
            dy = -math.sin(self.angle) * speed
            if not wall_at(self.x + dx, self.y): self.x += dx
            if not wall_at(self.x, self.y + dy): self.y += dy
        if keys[pygame.K_a]: self.angle -= 0.05
        if keys[pygame.K_d]: self.angle += 0.05

class Bullet:
    def __init__(self, x, y, angle):
        self.x, self.y = x, y
        self.angle = angle
        self.speed = 10
        self.alive = True

    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        if wall_at(self.x, self.y):
            self.alive = False

    def draw(self, player):
        pygame.draw.circle(screen, (255,255,0), (WIDTH//2, HEIGHT//2), 3)

class Enemy:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.health = 100
        self.alive = True

    def update(self, player):
        if not self.alive: return
        dx, dy = player.x - self.x, player.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 50:
            self.x += dx / dist
            self.y += dy / dist

    def draw(self, player):
        dx, dy = self.x - player.x, self.y - player.y
        distance = math.hypot(dx, dy)
        angle = math.atan2(dy, dx) - player.angle
        while angle < -math.pi: angle += 2*math.pi
        while angle > math.pi: angle -= 2*math.pi
        if -HALF_FOV < angle < HALF_FOV:
            proj_height = PROJ_COEFF / (distance + 0.0001)
            x = WIDTH // 2 + math.tan(angle) * DIST
            pygame.draw.rect(screen, (255, 0, 0), (x - 10, HEIGHT//2 - proj_height//2, 20, proj_height))
            if self.health < 100:
                pygame.draw.line(screen, (255,0,0), (x-10, HEIGHT//2 - proj_height//2 - 10), (x-10 + (self.health/100)*20, HEIGHT//2 - proj_height//2 - 10), 4)

def wall_at(x, y):
    grid_x, grid_y = int(x // TILE_SIZE), int(y // TILE_SIZE)
    if 0 <= grid_x < MAP_WIDTH and 0 <= grid_y < MAP_HEIGHT:
        return game_map[grid_y][grid_x] == 1
    return True

def draw_walls(player):
    screen.fill((40, 40, 40))
    pygame.draw.rect(screen, (30, 30, 30), (0, HEIGHT // 2, WIDTH, HEIGHT // 2))
    ox, oy, angle = player.x, player.y, player.angle
    for ray in range(NUM_RAYS):
        ray_angle = angle - HALF_FOV + ray * DELTA_ANGLE
        for depth in range(1, MAX_DEPTH):
            target_x = ox + depth * math.cos(ray_angle)
            target_y = oy + depth * math.sin(ray_angle)
            if wall_at(target_x, target_y):
                depth *= math.cos(angle - ray_angle)
                proj_height = PROJ_COEFF / (depth + 0.0001)
                color = (100 - min(int(depth * 0.1), 100),) * 3
                pygame.draw.rect(screen, color, (ray * SCALE, HEIGHT // 2 - proj_height // 2, SCALE, proj_height))
                break

def draw_ui(player):
    font = pygame.font.SysFont("Arial", 24)
    screen.blit(font.render(f"Health: {player.health}", True, (255,0,0)), (10,10))
    screen.blit(font.render(f"Ammo: {player.ammo}", True, (255,255,0)), (10,40))
    screen.blit(font.render(f"Score: {player.score}", True, (0,255,0)), (10,70))

def draw_menu(options, selected, title):
    screen.fill((0,0,0))
    font = pygame.font.SysFont("Arial", 48)
    screen.blit(font.render(title, True, (255,255,255)), (WIDTH//2-100, 100))
    font = pygame.font.SysFont("Arial", 32)
    for i, opt in enumerate(options):
        color = (255,255,0) if i == selected else (200,200,200)
        screen.blit(font.render(opt, True, color), (WIDTH//2 - 50, 200 + i * 50))

def execute_menu_action():
    global game_state, selected_option, player, bullets, enemies, running
    if game_state == 'menu':
        if selected_option == 0:
            game_state = 'playing'
            player = Player()
            bullets.clear()
            enemies[:] = [Enemy(TILE_SIZE*5, TILE_SIZE*5), Enemy(TILE_SIZE*7, TILE_SIZE*6)]
        else: running = False
    elif game_state == 'paused':
        if selected_option == 0: game_state = 'playing'
        else: running = False
    elif game_state == 'gameover':
        if selected_option == 0:
            game_state = 'playing'
            player = Player()
            bullets.clear()
            enemies[:] = [Enemy(TILE_SIZE*5, TILE_SIZE*5), Enemy(TILE_SIZE*7, TILE_SIZE*6)]
        else: running = False

def main():
    global game_state, selected_option, running
    player = Player()
    bullets = []
    enemies = [Enemy(TILE_SIZE*5, TILE_SIZE*5), Enemy(TILE_SIZE*7, TILE_SIZE*6)]
    while running:
        clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: running = False
            if game_state in ['menu','paused','gameover']:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_UP: selected_option = (selected_option - 1) % 2
                    elif e.key == pygame.K_DOWN: selected_option = (selected_option + 1) % 2
                    elif e.key == pygame.K_RETURN: execute_menu_action()
                elif e.type == pygame.MOUSEMOTION:
                    mx, my = e.pos
                    for i in range(2):
                        if pygame.Rect(WIDTH//2-100, 200 + i*50, 200, 40).collidepoint(mx, my):
                            selected_option = i
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    execute_menu_action()
            if game_state == 'playing' and e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    game_state = 'paused'
                    selected_option = 0
                elif e.key == pygame.K_SPACE and player.ammo > 0:
                    bullets.append(Bullet(player.x, player.y, player.angle))
                    shoot_sound.play()
                    player.ammo -= 1
        if game_state == 'playing':
            keys = pygame.key.get_pressed()
            player.movement(keys)
            for b in bullets[:]:
                b.update()
                for enemy in enemies:
                    if enemy.alive and math.hypot(b.x - enemy.x, b.y - enemy.y) < TILE_SIZE/2:
                        enemy.health -= 20
                        hit_sound.play()
                        b.alive = False
                        if enemy.health <= 0:
                            enemy.alive = False
                            player.score += 100
                if not b.alive: bullets.remove(b)
            for enemy in enemies: enemy.update(player)
            for enemy in enemies:
                if enemy.alive and math.hypot(enemy.x - player.x, enemy.y - player.y) < TILE_SIZE/2:
                    player.health -= 1
                    if player.health <= 0:
                        game_state = 'gameover'
                        selected_option = 0
            draw_walls(player)
            for enemy in enemies: enemy.draw(player)
            for bullet in bullets: bullet.draw(player)
            draw_ui(player)
        elif game_state == 'menu': draw_menu(menu_options, selected_option, "MAIN MENU")
        elif game_state == 'paused': draw_menu(pause_options, selected_option, "PAUSED")
        elif game_state == 'gameover': draw_menu(gameover_options, selected_option, "GAME OVER")
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
