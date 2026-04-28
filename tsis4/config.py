import pygame

# Database configuration
DB_HOST = "localhost"
DB_PORT = "5433"
DB_NAME = "snake_game"
DB_USER = "ernurzhubandykov"
DB_PASSWORD = ""  

# Game constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
CELL_SIZE = WINDOW_WIDTH // GRID_SIZE

# Colors (RGB)
BLACK = (0, 0, 0)           # Black color - used for background
WHITE = (255, 255, 255)     # White color - used for text and borders
RED = (255, 0, 0)           # Red color - used for danger indicators
GREEN = (0, 255, 0)         # Green color - used for normal food and snake
BLUE = (0, 0, 255)          # Blue color - used for slow motion power-up
YELLOW = (255, 255, 0)      # Yellow color - used for bonus food
PURPLE = (128, 0, 128)      # Purple color - used for shield power-up
ORANGE = (255, 165, 0)      # Orange color - used for timer-based food
DARK_RED = (139, 0, 0)      # Dark Red color - used for poison food
GRAY = (128, 128, 128)      # Gray color - used for wall obstacles
CYAN = (0, 255, 255)        # Cyan color - used for speed boost power-up

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Game settings
INITIAL_SPEED = 10
FOODS_PER_LEVEL = 5
SPEED_INCREMENT = 2