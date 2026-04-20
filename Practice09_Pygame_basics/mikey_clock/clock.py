import pygame
import datetime
import math
import sys


pygame.init()

WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Часы Микки")
clock = pygame.time.Clock()

try:
    background = pygame.image.load("mickeyclock.jpeg")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except:
    print("Ошибка: не удалось загрузить изображение mickeyclock.jpeg")
    print("Убедитесь, что файл находится в той же папке, что и программа")
    pygame.quit()
    sys.exit()

center_x, center_y = WIDTH // 2, HEIGHT // 2
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

def draw_hand(surface, color, length, width, angle, center_x, center_y):
    end_x = center_x + length * math.cos(math.radians(90 - angle))
    end_y = center_y - length * math.sin(math.radians(90 - angle))
    pygame.draw.line(surface, color, (center_x, center_y), (end_x, end_y), width)
    pygame.draw.circle(surface, color, (int(end_x), int(end_y)), width // 2)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    now = datetime.datetime.now()
    
    seconds = now.second + now.microsecond / 1000000.0
    second_angle = seconds * 6
    
    minutes = now.minute + now.second / 60.0
    minute_angle = minutes * 6
    
    screen.blit(background, (0, 0))
    
    draw_hand(screen, RED, 200, 4, second_angle, center_x, center_y)
    draw_hand(screen, BLUE, 160, 10, minute_angle, center_x, center_y)
    
    pygame.draw.circle(screen, (0, 0, 0), (center_x, center_y), 12)
    pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), 8)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()