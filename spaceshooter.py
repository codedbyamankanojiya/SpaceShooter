import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 50)
GRAY = (100, 100, 100)
CYAN = (0, 255, 255)

# Setup Display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter Deluxe")
clock = pygame.time.Clock()

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
        self.speed = 5
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        
        # Boundary checks
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 35), pygame.SRCALPHA)
        color = DIFFICULTY[current_difficulty]["enemy_color"]
        pygame.draw.ellipse(self.image, color, (0, 0, 40, 35))
        pygame.draw.circle(self.image, BLACK, (10, 10), 3) # Eye
        pygame.draw.circle(self.image, BLACK, (30, 10), 3) # Eye
        
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        
        speed_min, speed_max = DIFFICULTY[current_difficulty]["enemy_speed"]
        self.speed_y = random.randrange(speed_min, speed_max + 1)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT + 10:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            speed_min, speed_max = DIFFICULTY[current_difficulty]["enemy_speed"]
            self.speed_y = random.randrange(speed_min, speed_max + 1)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((8, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, YELLOW, (0, 0, 8, 16))
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speed_y = -10

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.bottom < 0:
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

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT:
            self.rect.x = random.randrange(WIDTH)
            self.rect.y = random.randrange(-20, -5)

# Game State Management
state = "MENU" # MENU, DIFFICULTY, PLAYING, GAME_OVER
score = 0
spawn_timer = 0

# Sprite Groups
all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
stars = pygame.sprite.Group()
player = None

# create stars once
for i in range(100):
    s = Star()
    stars.add(s)

def start_game():
    global state, score, player, spawn_timer
    state = "PLAYING"
    score = 0
    spawn_timer = 0
    
    # Clear game sprites but keep stars
    all_sprites.empty()
    mobs.empty()
    bullets.empty()
    
    player = Player()
    all_sprites.add(player)

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
while running:
    clock.tick(FPS)
    
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
                if event.key == pygame.K_SPACE:
                    player.shoot()
                if event.key == pygame.K_ESCAPE:
                    state = "MENU"
        elif state == "GAME_OVER":
            btn_menu.handle_event(event)

    # 2. Logic Update
    mouse_pos = pygame.mouse.get_pos()
    
    # Always update stars
    stars.update()

    if state == "MENU":
        btn_start.check_hover(mouse_pos)
        btn_quit.check_hover(mouse_pos)
    
    elif state == "DIFFICULTY":
        btn_easy.check_hover(mouse_pos)
        btn_normal.check_hover(mouse_pos)
        btn_hard.check_hover(mouse_pos)

    elif state == "PLAYING":
        all_sprites.update()

        # Spawning Logic
        spawn_timer += 1
        rate = DIFFICULTY[current_difficulty]["spawn_rate"]
        if spawn_timer >= rate:
            spawn_timer = 0
            m = Enemy()
            all_sprites.add(m)
            mobs.add(m)

        # Hits
        hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
        for hit in hits:
            score += 10
            # Respawn
            m = Enemy()
            all_sprites.add(m)
            mobs.add(m)
        
        # Player Hit
        hits = pygame.sprite.spritecollide(player, mobs, False)
        if hits:
            state = "GAME_OVER"

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

    elif state == "GAME_OVER":
        draw_text("GAME OVER", font_lg, RED, screen, WIDTH//2, 150)
        draw_text(f"Final Score: {score}", font_md, WHITE, screen, WIDTH//2, 250)
        btn_menu.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()