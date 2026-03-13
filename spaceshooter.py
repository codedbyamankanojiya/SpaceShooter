import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Gameplay tuning
PLAYER_SPEED = 350  # px/sec
PLAYER_SHOOT_DELAY_MS = 250
BULLET_SPEED = 700  # px/sec
ENEMY_SIZE = (40, 35)
ENEMY_SPEED_CAP_PX_S = 320
ENEMY_BASE_SPEED_PX_S = {
    "EASY": 90,
    "NORMAL": 130,
    "HARD": 180,
}
ENEMY_SPEED_RAMP_PX_S_PER_SEC = {
    "EASY": 3.0,
    "NORMAL": 5.0,
    "HARD": 7.0,
}
POWERUP_DROP_CHANCE = 0.12  # chance on enemy kill
POWERUP_MINUS_CHANCE = 0.20  # when a powerup spawns, chance it's a MINUS (rarer)
POWERUP_SPAWN_MIN_MS = 4500
POWERUP_SPAWN_MAX_MS = 8500
POWERUP_SPEED_PX_S = 180

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 50)
GRAY = (100, 100, 100)
CYAN = (0, 255, 255)

# Fonts
font_sm = pygame.font.Font(None, 24)
font_md = pygame.font.Font(None, 48)
font_lg = pygame.font.Font(None, 72)

# Difficulty Settings
DIFFICULTY = {
    "EASY": {"spawn_rate": 60, "enemy_speed": (1, 3), "enemy_color": GREEN},
    "NORMAL": {"spawn_rate": 40, "enemy_speed": (2, 5), "enemy_color": YELLOW},
    "HARD": {"spawn_rate": 20, "enemy_speed": (4, 8), "enemy_color": RED}
}
current_difficulty = "NORMAL"

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10) # Border
        
        text_surf = font_md.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if self.action:
                self.action()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, CYAN, [(25, 0), (50, 40), (0, 40)])
        pygame.draw.rect(self.image, WHITE, (20, 20, 10, 20)) # Engine detail
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 20
        self.speed = PLAYER_SPEED
        self.shoot_delay = PLAYER_SHOOT_DELAY_MS
        self.last_shot = pygame.time.get_ticks()
        self.bullet_count = 1
        self.double_shot = False

    def update(self, dt):
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT]:
            dx -= self.speed * dt
        if keys[pygame.K_RIGHT]:
            dx += self.speed * dt

        self.rect.x += int(dx)
        
        # Boundary checks
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

        if keys[pygame.K_SPACE]:
            self.shoot()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now

            def offsets_for_count(n):
                spread = 24
                if n <= 1:
                    return [0]
                return [int(-spread + (2 * spread) * i / (n - 1)) for i in range(n)]

            if self.double_shot:
                for lane_off in (-14, 14):
                    for off in offsets_for_count(self.bullet_count):
                        bullet = Bullet(self.rect.centerx + lane_off + off, self.rect.top)
                        all_sprites.add(bullet)
                        bullets.add(bullet)
            else:
                for off in offsets_for_count(self.bullet_count):
                    bullet = Bullet(self.rect.centerx + off, self.rect.top)
                    all_sprites.add(bullet)
                    bullets.add(bullet)

    def cycle_fire_mode(self):
        if self.double_shot:
            return

        if self.bullet_count < 4:
            self.bullet_count += 1
        else:
            self.double_shot = True

    def decrease_fire_mode(self):
        if self.double_shot:
            self.double_shot = False
            return

        if self.bullet_count > 1:
            self.bullet_count -= 1

    def fire_mode_label(self):
        return f"DOUBLE x{self.bullet_count}" if self.double_shot else f"x{self.bullet_count}"

class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed_px_s):
        super().__init__()
        self.image = pygame.Surface(ENEMY_SIZE, pygame.SRCALPHA)
        color = DIFFICULTY[current_difficulty]["enemy_color"]
        pygame.draw.ellipse(self.image, color, (0, 0, ENEMY_SIZE[0], ENEMY_SIZE[1]))
        pygame.draw.circle(self.image, BLACK, (10, 10), 3) # Eye
        pygame.draw.circle(self.image, BLACK, (30, 10), 3) # Eye
        
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)

        self.speed_y = float(speed_px_s)

    def update(self, dt):
        self.rect.y += int(self.speed_y * dt)
        if self.rect.top > HEIGHT + 10:
            self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((8, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, YELLOW, (0, 0, 8, 16))
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speed_y = -BULLET_SPEED

    def update(self, dt):
        self.rect.y += int(self.speed_y * dt)
        if self.rect.bottom < 0:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, kind="PLUS"):
        super().__init__()
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        self.kind = kind
        if kind == "MINUS":
            pygame.draw.circle(self.image, RED, (12, 12), 12)
            pygame.draw.circle(self.image, WHITE, (12, 12), 12, 2)
            pygame.draw.rect(self.image, WHITE, (6, 11, 12, 2))
        else:
            pygame.draw.circle(self.image, BLUE, (12, 12), 12)
            pygame.draw.circle(self.image, WHITE, (12, 12), 12, 2)
            pygame.draw.rect(self.image, WHITE, (11, 6, 2, 12))
            pygame.draw.rect(self.image, WHITE, (6, 11, 12, 2))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_y = POWERUP_SPEED_PX_S

    def update(self, dt):
        self.rect.y += int(self.speed_y * dt)
        if self.rect.top > HEIGHT + 20:
            self.kill()

class Star(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = random.randint(1, 3)
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH)
        self.rect.y = random.randrange(HEIGHT)
        self.speed_y = random.randrange(1, 10)

    def update(self, dt=0.0):
        self.rect.y += self.speed_y * dt
        if self.rect.top > HEIGHT:
            self.rect.x = random.randrange(WIDTH)
            self.rect.y = random.randrange(-20, -5)

# Game State Management
state = "MENU" # MENU, DIFFICULTY, PLAYING, GAME_OVER
score = 0
spawn_timer = 0
game_time_s = 0.0
next_powerup_spawn_ms = 0

# Sprite Groups
all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
stars = pygame.sprite.Group()
powerups = pygame.sprite.Group()
player = None

# create stars once
for i in range(100):
    s = Star()
    stars.add(s)

def start_game():
    global state, score, player, spawn_timer, game_time_s, next_powerup_spawn_ms
    state = "PLAYING"
    score = 0
    spawn_timer = 0
    game_time_s = 0.0
    next_powerup_spawn_ms = pygame.time.get_ticks() + random.randint(POWERUP_SPAWN_MIN_MS, POWERUP_SPAWN_MAX_MS)
    
    # Clear game sprites but keep stars
    all_sprites.empty()
    mobs.empty()
    bullets.empty()
    powerups.empty()
    
    player = Player()
    all_sprites.add(player)

def spawn_powerup(x, y):
    kind = "MINUS" if random.random() < POWERUP_MINUS_CHANCE else "PLUS"
    p = PowerUp(x, y, kind=kind)
    all_sprites.add(p)
    powerups.add(p)

def current_enemy_speed_px_s():
    base = ENEMY_BASE_SPEED_PX_S[current_difficulty]
    ramp = ENEMY_SPEED_RAMP_PX_S_PER_SEC[current_difficulty]
    speed = base + ramp * game_time_s
    speed = min(speed, ENEMY_SPEED_CAP_PX_S)
    jitter = random.uniform(-0.15, 0.15) * speed
    return max(40.0, speed + jitter)

def set_difficulty(diff):
    global current_difficulty
    current_difficulty = diff
    start_game()

def quit_game():
    pygame.quit()
    sys.exit()

def go_to_difficulty():
    global state
    state = "DIFFICULTY"

def go_to_menu():
    global state
    state = "MENU"

def draw_text(text, font, color, surface, x, y, align="center"):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    if align == "center":
        textrect.center = (x, y)
    elif align == "left":
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

# UI Elements
btn_start = Button(WIDTH//2 - 100, 250, 200, 50, "Start Game", GREEN, (100, 255, 100), go_to_difficulty)
btn_quit = Button(WIDTH//2 - 100, 350, 200, 50, "Quit", RED, (255, 100, 100), quit_game)

btn_easy = Button(WIDTH//2 - 100, 200, 200, 50, "Easy", GREEN, (100, 255, 100), lambda: set_difficulty("EASY"))
btn_normal = Button(WIDTH//2 - 100, 300, 200, 50, "Normal", YELLOW, (255, 255, 100), lambda: set_difficulty("NORMAL"))
btn_hard = Button(WIDTH//2 - 100, 400, 200, 50, "Hard", RED, (255, 100, 100), lambda: set_difficulty("HARD"))

btn_menu = Button(WIDTH//2 - 100, 400, 200, 50, "Main Menu", BLUE, (100, 100, 255), go_to_menu)

# Main Loop
running = True
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter Deluxe")
while running:
    dt = clock.tick(FPS) / 1000.0
    
    # 1. Event Handling
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        
        if state == "MENU":
            btn_start.handle_event(event)
            btn_quit.handle_event(event)
        elif state == "DIFFICULTY":
            btn_easy.handle_event(event)
            btn_normal.handle_event(event)
            btn_hard.handle_event(event)
        elif state == "PLAYING":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = "MENU"
        elif state == "GAME_OVER":
            btn_menu.handle_event(event)

    # 2. Logic Update
    mouse_pos = pygame.mouse.get_pos()
    
    # Always update stars
    stars.update(dt)

    if state == "MENU":
        btn_start.check_hover(mouse_pos)
        btn_quit.check_hover(mouse_pos)
    
    elif state == "DIFFICULTY":
        btn_easy.check_hover(mouse_pos)
        btn_normal.check_hover(mouse_pos)
        btn_hard.check_hover(mouse_pos)

    elif state == "PLAYING":
        game_time_s += dt
        all_sprites.update(dt)

        # Spawning Logic
        spawn_timer += 1
        rate = DIFFICULTY[current_difficulty]["spawn_rate"]
        if spawn_timer >= rate:
            spawn_timer = 0
            m = Enemy(current_enemy_speed_px_s())
            all_sprites.add(m)
            mobs.add(m)

        # Timed powerup spawns (in addition to drop chance)
        now_ms = pygame.time.get_ticks()
        if now_ms >= next_powerup_spawn_ms:
            next_powerup_spawn_ms = now_ms + random.randint(POWERUP_SPAWN_MIN_MS, POWERUP_SPAWN_MAX_MS)
            spawn_powerup(random.randint(30, WIDTH - 30), random.randint(-120, -40))

        # Hits
        hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
        for hit in hits:
            score += 10

            if random.random() < POWERUP_DROP_CHANCE:
                spawn_powerup(hit.rect.centerx, hit.rect.centery)
        
        # Player Hit
        hits = pygame.sprite.spritecollide(player, mobs, False)
        if hits:
            state = "GAME_OVER"

        # Enemy passed the player -> game over
        passed = any(m.rect.top > player.rect.bottom for m in mobs.sprites())
        if passed:
            state = "GAME_OVER"

        # Powerup pickup
        phits = pygame.sprite.spritecollide(player, powerups, True)
        if phits:
            for p in phits:
                if getattr(p, "kind", "PLUS") == "MINUS":
                    player.decrease_fire_mode()
                else:
                    player.cycle_fire_mode()

    elif state == "GAME_OVER":
        btn_menu.check_hover(mouse_pos)

    # 3. Drawing
    screen.fill(BLACK)
    stars.draw(screen) # Draw stars in background for all states

    if state == "MENU":
        draw_text("SPACE SHOOTER", font_lg, CYAN, screen, WIDTH//2, 100)
        draw_text("DELUXE VERSION", font_md, WHITE, screen, WIDTH//2, 160)
        btn_start.draw(screen)
        btn_quit.draw(screen)
        draw_text("Code by Antigravity", font_sm, GRAY, screen, WIDTH//2, HEIGHT - 30)

    elif state == "DIFFICULTY":
        draw_text("SELECT DIFFICULTY", font_md, WHITE, screen, WIDTH//2, 100)
        btn_easy.draw(screen)
        btn_normal.draw(screen)
        btn_hard.draw(screen)

    elif state == "PLAYING":
        all_sprites.draw(screen)
        draw_text(f"SCORE: {score}", font_md, WHITE, screen, WIDTH//2, 30)
        draw_text(f"Level: {current_difficulty}", font_sm, GRAY, screen, 60, 20)
        draw_text(f"Power: {player.fire_mode_label()}", font_sm, GRAY, screen, WIDTH - 150, 20, align="left")

    elif state == "GAME_OVER":
        draw_text("GAME OVER", font_lg, RED, screen, WIDTH//2, 150)
        draw_text(f"Final Score: {score}", font_md, WHITE, screen, WIDTH//2, 250)
        btn_menu.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()