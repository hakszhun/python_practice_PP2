import pygame
import sys
from player import MusicPlayer

pygame.init()

WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Music Player")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 150, 255)
GRAY = (200, 200, 200)

font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

player = MusicPlayer("music")

SONG_END = pygame.USEREVENT + 1
pygame.mixer.music.set_endevent(SONG_END)

def draw_ui():
    screen.fill(WHITE)
    
    title = font.render("Music Player", True, BLUE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
    
    current_song = player.get_current_track_name()
    song_text = small_font.render(f"Now Playing: {current_song}", True, BLACK)
    screen.blit(song_text, (WIDTH//2 - song_text.get_width()//2, 100))
    
    playlist_info = small_font.render(player.get_playlist_info(), True, GRAY)
    screen.blit(playlist_info, (WIDTH//2 - playlist_info.get_width()//2, 140))
    
    controls = [
        "P - Play",
        "S - Stop",
        "N - Next Track",
        "B - Previous Track",
        "Q - Quit"
    ]
    
    y_offset = 200
    for control in controls:
        text = small_font.render(control, True, BLACK)
        screen.blit(text, (50, y_offset))
        y_offset += 30


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == SONG_END:
            if not player.is_stopped:
                player.next_track()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                player.play()
            elif event.key == pygame.K_s:
                player.stop()
            elif event.key == pygame.K_n:
                player.next_track()
            elif event.key == pygame.K_b:
                player.previous_track()
            elif event.key == pygame.K_q:
                running = False
    
    draw_ui()
    pygame.display.flip()
    clock.tick(60)

