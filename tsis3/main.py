import pygame
import sys
import os
import random
from racer import Coin
from persistence import load_settings, save_settings, load_leaderboard, save_score
from ui import Button, TextInput
from racer import Player, Enemy, Obstacle, PowerUp

# --- AUTO-FIX PATHING ---
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# --- Initialization ---
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS 3: Racer")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
coins = pygame.sprite.Group()
settings = load_settings()




def load_sound(name):
    # Получаем путь к папке assets (файлы прямо в ней)
    current_dir = os.path.dirname(os.path.abspath(__file__))  # tsis3
    assets_dir = os.path.join(current_dir, 'assets')  # tsis3/assets
    full_path = os.path.join(assets_dir, name)  # tsis3/assets/crash.wav
    
    print(f"Trying to load sound: {full_path}")  # для отладки
    
    if not os.path.exists(full_path):
        print(f"ERROR: Sound not found - {full_path}")
        return None
    
    try:
        sound = pygame.mixer.Sound(full_path)
        return sound
    except pygame.error as e:
        print(f"Failed to load sound {name}: {e}")
        return None

snd_crash = load_sound('crash.wav')
snd_powerup = load_sound('powerup.wav')

music_loaded = False
try:
  
    current_dir = os.path.dirname(os.path.abspath(__file__))
    music_path = os.path.join(current_dir, 'assets', 'powerup.mp3')
    pygame.mixer.music.load(music_path)
    music_loaded = True
    print(f"Music loaded successfully from: {music_path}")
except Exception as e:
    print(f"Failed to load music: {e}")
    pass

# --- Global Variables ---
state = "MENU"
player_name = "Player"
score = 0
distance = 0
level = 1
level_progress = 0
LEVEL_BASE = 1000  # base points for level

all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
powerups = pygame.sprite.Group()
coins = pygame.sprite.Group()

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.value = random.choice([1, 2, 5])  # weighted values
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)  # allow transparency
        self.color = (255, 215, 0) if self.value == 1 else (0,255,0) if self.value == 2 else (255,0,255)

        # draw circle instead of square
        pygame.draw.circle(self.image, self.color, (10, 10), 10)
        self.rect = self.image.get_rect()
        self.rect.x = random.choice([180, 260, 340])
        self.rect.y = -20
        self.speed = 4

    def update(self):
        self.rect.y += self.speed

player = None

def reset_game():
    global player, score, distance, all_sprites, enemies, obstacles, powerups, coins, level, level_progress
    all_sprites.empty()
    enemies.empty()
    obstacles.empty()
    powerups.empty()
    coins.empty()
    player = Player(settings["car_color"])
    all_sprites.add(player)
    score = 0
    distance = 0
    level = 1
    level_progress = 0
    if music_loaded and settings["sound"]:
        pygame.mixer.music.play(-1)

def draw_hud():
    screen.blit(font.render(f"Score: {int(score)}", True, (255,255,255)), (10, 10))
    screen.blit(font.render(f"Dist: {int(distance)}m", True, (255,255,255)), (10, 40))
    if player and player.nitro_active:
        time_left = (player.powerup_timer - pygame.time.get_ticks()) // 1000
        screen.blit(font.render(f"NITRO: {max(0, time_left)}s", True, (0, 255, 255)), (10, 80))
    if player and player.shield_active:
        screen.blit(font.render("SHIELD ACTIVE", True, (255, 215, 0)), (10, 80))

def draw_level_bar():
    # background bar
    pygame.draw.rect(screen, (100,100,100), (150, 560, 300, 20))
    # progress fill
    current_threshold = LEVEL_BASE * level
    progress_width = int((level_progress / current_threshold) * 300)
    pygame.draw.rect(screen, (0,255,0), (150, 560, progress_width, 20))
    # level text
    txt = font.render(f"Level {level}", True, (255,255,255))
    screen.blit(txt, (250, 530))

# UI Setup
btn_play = Button(200, 150, 200, 50, "Play")
btn_board = Button(200, 220, 200, 50, "Leaderboard")
btn_settings = Button(200, 290, 200, 50, "Settings")
btn_quit = Button(200, 360, 200, 50, "Quit")
btn_back = Button(200, 500, 200, 50, "Back")
btn_retry = Button(200, 350, 200, 50, "Retry")
btn_menu = Button(200, 420, 200, 50, "Main Menu")
name_input = TextInput(200, 250, 200, 40)

# Spawn Timers
SPAWN_ENEMY = pygame.USEREVENT + 1
SPAWN_OBSTACLE = pygame.USEREVENT + 2
SPAWN_POWERUP = pygame.USEREVENT + 3
pygame.time.set_timer(SPAWN_ENEMY, 1500)
pygame.time.set_timer(SPAWN_OBSTACLE, 2500)
pygame.time.set_timer(SPAWN_POWERUP, 6000)
SPAWN_COIN = pygame.USEREVENT + 4
pygame.time.set_timer(SPAWN_COIN, 1200)

running = True
while running:
    # Отрисовка трассы всегда (как фон)
    screen.fill((50, 150, 50)) 
    pygame.draw.rect(screen, (40, 40, 40), (150, 0, 300, 600)) 
    for y in range(0, 600, 40):
        pygame.draw.rect(screen, (255, 255, 255), (245, (y + int(distance * 10)) % 600, 10, 20))
        pygame.draw.rect(screen, (255, 255, 255), (345, (y + int(distance * 10)) % 600, 10, 20))

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        
        if state == "MENU":
            if btn_play.is_clicked(event): state = "NAME_INPUT"
            if btn_board.is_clicked(event): state = "LEADERBOARD"
            if btn_settings.is_clicked(event): state = "SETTINGS"
            if btn_quit.is_clicked(event): running = False
        
        elif state == "NAME_INPUT":
            name_input.handle_event(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                player_name = name_input.text if name_input.text else "Player"
                reset_game()
                state = "PLAY"

        elif state == "PLAY":
            if event.type == SPAWN_ENEMY:
                e = Enemy(settings["difficulty"])
                e.speed += level * 0.5
                if not pygame.sprite.spritecollideany(e, enemies):
                    all_sprites.add(e)
                    enemies.add(e)
            if event.type == SPAWN_OBSTACLE:
                o = Obstacle()
                if not pygame.sprite.spritecollideany(o, enemies) and not pygame.sprite.spritecollideany(o, obstacles):
                    all_sprites.add(o)
                    obstacles.add(o)
            if event.type == SPAWN_POWERUP:
                p = PowerUp()
                if not pygame.sprite.spritecollideany(p, enemies) and not pygame.sprite.spritecollideany(p, obstacles):
                    all_sprites.add(p)
                    powerups.add(p)
            if event.type == SPAWN_COIN:
                c = Coin()
                all_sprites.add(c)
                coins.add(c)

        elif state in ["LEADERBOARD", "SETTINGS"]:
            if btn_back.is_clicked(event): state = "MENU"

        elif state == "GAMEOVER":
            if btn_retry.is_clicked(event):
                reset_game()
                state = "PLAY"
            if btn_menu.is_clicked(event): state = "MENU"

    # Рендеринг экрана
    if state == "MENU":
        btn_play.draw(screen)
        btn_board.draw(screen)
        btn_settings.draw(screen)
        btn_quit.draw(screen)
        
    elif state == "NAME_INPUT":
        screen.blit(font.render("Enter Name & Press Enter:", True, (255,255,255)), (150, 200))
        name_input.draw(screen)

    elif state == "SETTINGS":
        screen.fill((40, 40, 40))
        screen.blit(font.render("SETTINGS", True, (255,255,255)), (240, 100))
        screen.blit(font.render(f"Difficulty: {settings['difficulty']}", True, (200,200,200)), (200, 200))
        btn_back.draw(screen)

    elif state == "PLAY":
        all_sprites.update()
        
        # Динамическая скорость
        keys = pygame.key.get_pressed()
        move_mod = 0
        if keys[pygame.K_UP]: move_mod = 0.08
        if keys[pygame.K_DOWN]: move_mod = -0.04
        
        distance += max(0.02, (0.1 + (score // 500 * 0.02) + move_mod))
        score += 0.2 if not player.nitro_active else 0.5
        current_threshold = LEVEL_BASE * level  # each level harder
        level_progress += 1  # steady progress

        if level_progress >= current_threshold:
            level += 1
            level_progress = 0  # reset to start of next level
            # increase difficulty
            for e in enemies:
                e.speed += 1
        
        # Коллизии
        if not player.shield_active:
            if pygame.sprite.spritecollideany(player, enemies) or pygame.sprite.spritecollideany(player, obstacles):
                if settings["sound"] and snd_crash: snd_crash.play()
                if player.crashes_allowed > 0:
                    player.crashes_allowed -= 1
                    player.shield_active = True
                    player.powerup_timer = pygame.time.get_ticks() + 2000
                else:
                    pygame.mixer.music.stop()
                    save_score(player_name, int(score), int(distance))
                    state = "GAMEOVER"

        # Бонусы
        hits = pygame.sprite.spritecollide(player, powerups, True)
        for hit in hits:
            if settings["sound"] and snd_powerup: snd_powerup.play()
            if hit.type == "Nitro":
                player.nitro_active, player.shield_active = True, False
                player.powerup_timer = pygame.time.get_ticks() + 4000
            elif hit.type == "Shield":
                player.shield_active, player.nitro_active = True, False
                player.powerup_timer = pygame.time.get_ticks() + 4000
            elif hit.type == "Repair": player.crashes_allowed = 1

        coin_hits = pygame.sprite.spritecollide(player, coins, True)
        for coin in coin_hits:
            score += coin.value * 10

            # increase enemy speed slightly
            for e in enemies:
                e.speed += 0.2

        all_sprites.draw(screen)
        draw_hud()
        draw_level_bar()

    elif state == "LEADERBOARD":
        screen.fill((30, 30, 30))
        board = load_leaderboard()
        for i, entry in enumerate(board):
            txt = f"{i+1}. {entry['name']} - {entry['score']} pts"
            screen.blit(font.render(txt, True, (255,255,255)), (150, 50 + i*35))
        btn_back.draw(screen)

    elif state == "GAMEOVER":
        screen.fill((0, 0, 0))
        screen.blit(font.render(f"GAME OVER! Score: {int(score)}", True, (255, 0, 0)), (180, 200))
        btn_retry.draw(screen)
        btn_menu.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()