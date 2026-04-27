import pygame
import math
from collections import deque


def flood_fill(surface, x, y, fill_color):
    target = surface.get_at((x, y))[:3]
    fill = tuple(fill_color[:3])
    if target == fill:
        return
    w, h = surface.get_size()
    seen = set()
    queue = deque([(x, y)])
    seen.add((x, y))
    while queue:
        cx, cy = queue.popleft()
        surface.set_at((cx, cy), fill)
        for nx, ny in ((cx-1,cy),(cx+1,cy),(cx,cy-1),(cx,cy+1)):
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen:
                if surface.get_at((nx, ny))[:3] == target:
                    seen.add((nx, ny))
                    queue.append((nx, ny))


def draw_rectangle(surface, start, end, color, width):
    x = min(start[0], end[0])
    y = min(start[1], end[1])
    w = abs(end[0] - start[0])
    h = abs(end[1] - start[1])
    if w > 0 and h > 0:
        pygame.draw.rect(surface, color, (x, y, w, h), width)


def draw_circle(surface, start, end, color, width):
    cx = (start[0] + end[0]) // 2
    cy = (start[1] + end[1]) // 2
    r = int(math.hypot(end[0]-start[0], end[1]-start[1]) / 2)
    if r > 0:
        pygame.draw.circle(surface, color, (cx, cy), r, width)


def draw_square(surface, start, end, color, width):
    side = min(abs(end[0]-start[0]), abs(end[1]-start[1]))
    sx = start[0] + (side if end[0] >= start[0] else -side)
    sy = start[1] + (side if end[1] >= start[1] else -side)
    draw_rectangle(surface, start, (sx, sy), color, width)


def draw_right_triangle(surface, start, end, color, width):
    pts = [start, (start[0], end[1]), end]
    pygame.draw.polygon(surface, color, pts, width)


def draw_equilateral_triangle(surface, start, end, color, width):
    mx = (start[0] + end[0]) / 2
    base = abs(end[0] - start[0])
    h = base * math.sqrt(3) / 2
    pts = [(int(mx), start[1]), (start[0], int(start[1]+h)), (end[0], int(start[1]+h))]
    pygame.draw.polygon(surface, color, pts, width)


def draw_rhombus(surface, start, end, color, width):
    mx = (start[0] + end[0]) // 2
    my = (start[1] + end[1]) // 2
    pts = [(mx, start[1]), (end[0], my), (mx, end[1]), (start[0], my)]
    pygame.draw.polygon(surface, color, pts, width)


SHAPES = {
    2: draw_rectangle,
    3: draw_circle,
    4: draw_square,
    5: draw_right_triangle,
    6: draw_equilateral_triangle,
    7: draw_rhombus,
}