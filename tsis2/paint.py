"""
paint.py — TSIS 2
Keys:
  L=Pencil, N=Straight line, Z=Rect, X=Circle, Q=Square,
  W=Right tri, E=Equil tri, R=Rhombus, F=Fill, T=Text, C=Eraser, A=Clear
  1/2/3 = brush size   Ctrl+S = save PNG
Colors: click colored squares in the top-left corner
"""

import pygame
import datetime
from tools import flood_fill, SHAPES

pygame.init()

W, H = 1000, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Paint simulator")
clock = pygame.time.Clock()

canvas = pygame.Surface((W, H))
canvas.fill((0, 0, 0))

BRUSH_SIZES = [2, 5, 10]
brush_idx = 1

COLORS = {
    'white':  (255, 255, 255),
    'red':    (220, 50,  50),
    'green':  (50,  200, 80),
    'blue':   (50,  120, 220),
    'yellow': (240, 200, 40),
    'erase':  (0,   0,   0),
}

color = (255, 255, 255)   # current draw color

# Color buttons (top-left strip)
color_buttons = []
for i, (name, rgb) in enumerate(COLORS.items()):
    rect = pygame.Rect(5 + i * 38, 5, 32, 32)
    color_buttons.append((rect, rgb))

# Modes: 1=pencil, 2-7=shapes, 8=line, 9=fill, 10=text
mode = 1
SHAPE_MODES = (2, 3, 4, 5, 6, 7, 8)

fig_start = None
preview_end = None
is_drawing = False
pencil_last = None

text_active = False
text_pos = (0, 0)
text_buf = ""
font = pygame.font.SysFont("consolas", 28)

MODE_NAMES = {
    1:  "L  - Pencil       (draw freely)",
    2:  "Z  - Rectangle    (drag to draw)",
    3:  "X  - Circle       (drag to draw)",
    4:  "Q  - Square       (drag to draw)",
    5:  "W  - Right Tri    (drag to draw)",
    6:  "E  - Equil Tri    (drag to draw)",
    7:  "R  - Rhombus      (drag to draw)",
    8:  "N  - Straight Line (drag to draw)",
    9:  "F  - Flood Fill   (click region)",
    10: "T  - Text         (click, type, Enter)",
}

font_ui = pygame.font.SysFont("consolas", 14)

def draw_ui():
    # ── Color buttons ──────────────────────────────────
    for rect, rgb in color_buttons:
        pygame.draw.rect(screen, rgb, rect)
        pygame.draw.rect(screen, (150, 150, 150), rect, 1)

    # ── Status bar (brush + active mode name) ──────────
    mode_label = MODE_NAMES.get(mode, "")
    info = f"  Brush: {BRUSH_SIZES[brush_idx]}px  |  Active: {mode_label}"
    surf = font_ui.render(info, True, (255, 255, 100), (20, 20, 20))
    screen.blit(surf, (0, 42))

    # Help panel (bottom-right corner) 
    help_lines = [
        "--- TOOLS ---",
        "L  Pencil",
        "N  Straight Line",
        "Z  Rectangle",
        "X  Circle",
        "Q  Square",
        "W  Right Triangle",
        "E  Equil Triangle",
        "R  Rhombus",
        "F  Flood Fill",
        "T  Text",
        "C  Eraser",
        "A  Clear all",
        "",
        "--- BRUSH SIZE ---",
        "1=small  2=med  3=large",
        "",
        "--- OTHER ---",
        "Ctrl+S  Save PNG",
        "Esc     Quit",
    ]

    panel_w = 210
    line_h  = 16
    panel_h = len(help_lines) * line_h + 10
    px = W - panel_w - 4
    py = H - panel_h - 4

    # Semi-transparent background
    bg = pygame.Surface((panel_w, panel_h))
    bg.set_alpha(180)
    bg.fill((20, 20, 20))
    screen.blit(bg, (px, py))

    for i, line in enumerate(help_lines):
        # Highlight the currently active tool line
        active_key = MODE_NAMES.get(mode, "")[:1]   # e.g. "L"
        highlight = line.startswith(active_key + " ") and active_key != "-"
        fg = (255, 255, 100) if highlight else (200, 200, 200)
        txt = font_ui.render(line, True, fg)
        screen.blit(txt, (px + 6, py + 5 + i * line_h))

running = True
while running:
    mouse = pygame.mouse.get_pos()
    pressed = pygame.key.get_pressed()
    ctrl = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Keyboard 
        if event.type == pygame.KEYDOWN:

            if text_active:
                if event.key == pygame.K_RETURN:
                    canvas.blit(font.render(text_buf, True, color), text_pos)
                    text_active = False
                    text_buf = ""
                elif event.key == pygame.K_ESCAPE:
                    text_active = False
                    text_buf = ""
                elif event.key == pygame.K_BACKSPACE:
                    text_buf = text_buf[:-1]
                elif event.unicode and event.unicode.isprintable():
                    text_buf += event.unicode
                continue

            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_s and ctrl:
                fname = "canvas_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
                pygame.image.save(canvas, fname)
                print("Saved:", fname)

            if event.key == pygame.K_1: brush_idx = 0
            elif event.key == pygame.K_2: brush_idx = 1
            elif event.key == pygame.K_3: brush_idx = 2

            elif event.key == pygame.K_l: mode = 1
            elif event.key == pygame.K_z: mode = 2
            elif event.key == pygame.K_x: mode = 3
            elif event.key == pygame.K_q: mode = 4
            elif event.key == pygame.K_w: mode = 5
            elif event.key == pygame.K_e: mode = 6
            elif event.key == pygame.K_r: mode = 7
            elif event.key == pygame.K_n: mode = 8
            elif event.key == pygame.K_f: mode = 9
            elif event.key == pygame.K_t: mode = 10
            elif event.key == pygame.K_c: color = (0, 0, 0)
            elif event.key == pygame.K_a: canvas.fill((0, 0, 0))

        # Mouse Down 
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check color buttons
            for rect, rgb in color_buttons:
                if rect.collidepoint(mouse):
                    color = rgb

            is_drawing = True

            if mode in SHAPE_MODES:
                fig_start = mouse
                preview_end = mouse

            elif mode == 1:
                pencil_last = mouse

            elif mode == 9:
                flood_fill(canvas, mouse[0], mouse[1], color)

            elif mode == 10:
                text_active = True
                text_pos = mouse
                text_buf = ""

        # ── Mouse Motion ──────────────────────────────────
        if event.type == pygame.MOUSEMOTION:
            if is_drawing:
                bw = BRUSH_SIZES[brush_idx]
                if mode == 1 and pencil_last:
                    pygame.draw.line(canvas, color, pencil_last, mouse, bw)
                    pencil_last = mouse
                elif mode in SHAPE_MODES:
                    preview_end = mouse

        # Mouse Up 
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            bw = BRUSH_SIZES[brush_idx]
            if is_drawing and fig_start:
                if mode == 8:
                    pygame.draw.line(canvas, color, fig_start, mouse, bw)
                elif mode in SHAPES:
                    SHAPES[mode](canvas, fig_start, mouse, color, bw)
            is_drawing = False
            fig_start = None
            preview_end = None
            pencil_last = None

    # Draw 
    screen.blit(canvas, (0, 0))

    # Live preview
    if is_drawing and fig_start and preview_end:
        bw = BRUSH_SIZES[brush_idx]
        tmp = canvas.copy()
        if mode == 8:
            pygame.draw.line(tmp, color, fig_start, preview_end, bw)
        elif mode in SHAPES:
            SHAPES[mode](tmp, fig_start, preview_end, color, bw)
        screen.blit(tmp, (0, 0))

    # Text preview
    if text_active:
        preview_txt = font.render(text_buf + "|", True, color)
        screen.blit(preview_txt, text_pos)

    draw_ui()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()