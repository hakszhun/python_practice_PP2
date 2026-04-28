import pygame
import random
import sys
from config import *
from db import Database


class Food:
    def __init__(self, x, y, food_type="normal"):
        self.x = x
        self.y = y
        self.type = food_type
        self.spawn_time = pygame.time.get_ticks()
        self.duration = 5000 if food_type == "timer" else None

    def get_color(self):
        colors = {
            "normal": GREEN,
            "bonus":  YELLOW,
            "timer":  ORANGE,
            "poison": DARK_RED,
        }
        return colors.get(self.type, GREEN)

    def get_points(self):
        points = {
            "normal": 1,
            "bonus":  3,
            "timer":  2,
            "poison": 0,
        }
        return points.get(self.type, 1)

    def is_expired(self):
        if self.duration and self.type == "timer":
            return pygame.time.get_ticks() - self.spawn_time > self.duration
        return False


class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.type = power_type
        self.spawn_time = pygame.time.get_ticks()
        self.duration = 8000  # disappears from field after 8 s if not collected

    def get_color(self):
        colors = {
            "speed_boost": CYAN,
            "slow_motion": BLUE,
            "shield":      PURPLE,
        }
        return colors.get(self.type, WHITE)

    def get_effect(self):
        effects = {
            "speed_boost": {"speed_multiplier": 1.5, "duration": 5000},
            "slow_motion": {"speed_multiplier": 0.7, "duration": 5000},
            "shield":      {"shield": True,           "duration": None},
        }
        return effects.get(self.type)

    def is_expired(self):
        return pygame.time.get_ticks() - self.spawn_time > self.duration


class Obstacle:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_color(self):
        return GRAY


class Snake:
    def __init__(self):
        # Start with 3 segments so poison doesn't kill immediately
        cx, cy = GRID_SIZE // 2, GRID_SIZE // 2
        self.body = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = RIGHT
        self.grow = False
        self.shield = False
        self.active_effects = {}

    def move(self):
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def check_collision(self, obstacles):
        head = self.body[0]

        # Wall collision — always game over, shield does NOT protect from walls
        if head[0] < 0 or head[0] >= GRID_SIZE or head[1] < 0 or head[1] >= GRID_SIZE:
            return True

        # Self collision — shield absorbs once
        if head in self.body[1:]:
            if self.shield:
                self.shield = False
                return False
            return True

        # Obstacle collision — shield absorbs once
        obstacle_set = {(obs.x, obs.y) for obs in obstacles}
        if head in obstacle_set:
            if self.shield:
                self.shield = False
                return False
            return True

        return False

    def eat_food(self, food_type):
        # BUG FIX: poison must NOT set grow=True — snake should shrink, not grow
        if food_type == "poison":
            # Remove 2 segments from tail
            for _ in range(2):
                if len(self.body) > 1:
                    self.body.pop()
            # Game over if length drops to 1 or less
            return len(self.body) <= 1
        else:
            self.grow = True
            return False

    def activate_powerup(self, powerup):
        effect = powerup.get_effect()
        if "speed_multiplier" in effect:
            self.active_effects["speed"] = {
                "multiplier": effect["speed_multiplier"],
                "end_time":   pygame.time.get_ticks() + effect["duration"],
            }
        elif "shield" in effect:
            self.shield = True
        return True

    def update_effects(self):
        current_time = pygame.time.get_ticks()
        if "speed" in self.active_effects:
            if current_time > self.active_effects["speed"]["end_time"]:
                del self.active_effects["speed"]

    def get_speed_multiplier(self):
        if "speed" in self.active_effects:
            return self.active_effects["speed"]["multiplier"]
        return 1.0


class Game:
    def __init__(self, username, settings_manager):
        self.username = username
        self.settings_manager = settings_manager
        self.db = Database()
        self.personal_best = self.db.get_personal_best(username)

        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()

        self.reset_game()

    # Minimum food items always present on the field
    MIN_FOODS = 3

    def reset_game(self):
        self.snake = Snake()
        self.foods = []
        self.powerups = []
        self.obstacles = []
        self.score = 0
        self.level = 1
        self.food_eaten = 0
        self.game_over = False

        # Spawn MIN_FOODS items so the field isn't empty at start
        for _ in range(self.MIN_FOODS):
            self.spawn_food()

    # Spawning helpers
    def spawn_food(self):
        available = self.get_available_positions()
        if not available:
            return

        x, y = random.choice(available)

        rand = random.random()
        if rand < 0.60:
            food_type = "normal"
        elif rand < 0.80:
            food_type = "bonus"
        elif rand < 0.90:
            food_type = "timer"
        else:
            food_type = "poison"

        self.foods.append(Food(x, y, food_type))

    def spawn_powerup(self):
        # BUG FIX: requirement says only ONE power-up on field at a time
        if self.powerups:
            return

        available = self.get_available_positions()
        if not available:
            return

        x, y = random.choice(available)
        power_type = random.choice(["speed_boost", "slow_motion", "shield"])
        self.powerups.append(PowerUp(x, y, power_type))

    def spawn_obstacles(self):
        """
        Place wall blocks randomly, guaranteeing the snake's head has
        at least one reachable neighbour (not completely surrounded).
        """
        num_obstacles = min(5 + self.level, 15)
        self.obstacles = []

        # Positions the snake currently occupies — never block these
        snake_set = set(self.snake.body)
        # Also protect the 4 cells around the head so snake isn't instantly trapped
        head = self.snake.body[0]
        protected = snake_set | {
            (head[0] + dx, head[1] + dy)
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))
        }

        candidates = [
            (x, y)
            for x in range(GRID_SIZE)
            for y in range(GRID_SIZE)
            if (x, y) not in protected
        ]
        random.shuffle(candidates)

        for pos in candidates[:num_obstacles]:
            self.obstacles.append(Obstacle(*pos))

    def get_available_positions(self, include_snake=True):
        taken = set()
        for obs in self.obstacles:
            taken.add((obs.x, obs.y))
        for food in self.foods:
            taken.add((food.x, food.y))
        for powerup in self.powerups:
            taken.add((powerup.x, powerup.y))
        if include_snake:
            for seg in self.snake.body:
                taken.add(seg)

        return [
            (x, y)
            for x in range(GRID_SIZE)
            for y in range(GRID_SIZE)
            if (x, y) not in taken
        ]

    # Game loop
  

    def update(self):
        if self.game_over:
            return

        self.snake.update_effects()
        self.snake.move()

        if self.snake.check_collision(self.obstacles):
            self.game_over = True
            self.save_result()
            return

        head = self.snake.body[0]

        # Food collision
        for food in self.foods[:]:
            if (head[0] == food.x) and (head[1] == food.y):
                died = self.snake.eat_food(food.type)
                self.score += food.get_points()
                self.foods.remove(food)

                if died:
                    self.game_over = True
                    self.save_result()
                    return

                # Only count non-poison food toward level progress
                if food.type != "poison":
                    self.food_eaten += 1
                    if self.food_eaten >= FOODS_PER_LEVEL:
                        self.level_up()  # resets food_eaten to 0

                break  # only one food per frame

        # Power-up collision
        for powerup in self.powerups[:]:
            if (head[0] == powerup.x) and (head[1] == powerup.y):
                self.snake.activate_powerup(powerup)
                self.powerups.remove(powerup)
                break

        # Remove expired items
        self.foods    = [f for f in self.foods    if not f.is_expired()]
        self.powerups = [p for p in self.powerups if not p.is_expired()]

        # Always keep MIN_FOODS on the field (refill after eating or expiry)
        while len(self.foods) < self.MIN_FOODS:
            self.spawn_food()

        # Spawn power-up randomly (5% chance per frame, only one at a time)
        if not self.powerups and random.random() < 0.05:
            self.spawn_powerup()

    def level_up(self):
        self.level += 1
        self.food_eaten = 0  # reset counter for next level
        # Obstacles appear starting from level 3, refreshed every level
        if self.level >= 3:
            self.spawn_obstacles()

    def save_result(self):
        self.db.save_game_result(self.username, self.score, self.level)

    def get_speed(self):
        base_speed = INITIAL_SPEED + (self.level - 1) * SPEED_INCREMENT
        return max(1, int(base_speed * self.snake.get_speed_multiplier()))

 
    # Drawing


    def draw_grid(self):
        if not self.settings_manager.get("grid_overlay"):
            return
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, (50, 50, 50), (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, (50, 50, 50), (0, y), (WINDOW_WIDTH, y))

    def draw(self):
        self.screen.fill(BLACK)

        # Obstacles
        for obs in self.obstacles:
            rect = pygame.Rect(obs.x * CELL_SIZE, obs.y * CELL_SIZE,
                               CELL_SIZE - 1, CELL_SIZE - 1)
            pygame.draw.rect(self.screen, obs.get_color(), rect)

        # Foods
        font_small = pygame.font.Font(None, 20)
        for food in self.foods:
            rect = pygame.Rect(food.x * CELL_SIZE, food.y * CELL_SIZE,
                               CELL_SIZE - 1, CELL_SIZE - 1)
            pygame.draw.rect(self.screen, food.get_color(), rect)
            if food.type == "timer":
                remaining = max(0, (food.spawn_time + food.duration
                                    - pygame.time.get_ticks()) / 1000)
                txt = font_small.render(f"{int(remaining)}s", True, WHITE)
                self.screen.blit(txt, (food.x * CELL_SIZE + 3,
                                       food.y * CELL_SIZE + 3))

        # Power-ups — draw with a small letter label so player knows what it is
        font_label = pygame.font.Font(None, 18)
        labels = {"speed_boost": "S+", "slow_motion": "S-", "shield": "SH"}
        for pu in self.powerups:
            rect = pygame.Rect(pu.x * CELL_SIZE, pu.y * CELL_SIZE,
                               CELL_SIZE - 1, CELL_SIZE - 1)
            pygame.draw.rect(self.screen, pu.get_color(), rect)
            lbl = font_label.render(labels.get(pu.type, "?"), True, BLACK)
            self.screen.blit(lbl, (pu.x * CELL_SIZE + 2, pu.y * CELL_SIZE + 4))

        # Snake
        snake_color = tuple(int(c) for c in self.settings_manager.get("snake_color"))
        # BUG FIX: original used // 1.5 which is invalid (float divisor) → use int()
        body_color = (
            max(0, snake_color[0] - 80),
            max(0, snake_color[1] - 80),
            max(0, snake_color[2] - 80),
        )
        for i, seg in enumerate(self.snake.body):
            # Skip drawing segments that are outside the grid (wall collision frame)
            if seg[0] < 0 or seg[0] >= GRID_SIZE or seg[1] < 0 or seg[1] >= GRID_SIZE:
                continue
            rect = pygame.Rect(seg[0] * CELL_SIZE, seg[1] * CELL_SIZE,
                               CELL_SIZE - 1, CELL_SIZE - 1)
            color = snake_color if i == 0 else body_color
            pygame.draw.rect(self.screen, color, rect)
            # Shield glow on head
            if i == 0 and self.snake.shield:
                pygame.draw.rect(self.screen, PURPLE, rect, 2)

        self.draw_grid()

        # HUD
        font = pygame.font.Font(None, 36)
        self.screen.blit(font.render(f"Score: {self.score}",                        True, WHITE),  (10, 10))
        self.screen.blit(font.render(f"Level: {self.level}",                        True, WHITE),  (10, 50))
        self.screen.blit(font.render(f"Best:  {self.personal_best}",                True, WHITE),  (10, 90))
        self.screen.blit(font.render(f"Food:  {self.food_eaten}/{FOODS_PER_LEVEL}", True, WHITE),  (10, 130))

        y_off = 170
        if self.snake.shield:
            self.screen.blit(font.render("SHIELD ACTIVE", True, PURPLE), (10, y_off))
            y_off += 40

        if "speed" in self.snake.active_effects:
            eff = self.snake.active_effects["speed"]
            rem = max(0, (eff["end_time"] - pygame.time.get_ticks()) / 1000)
            if eff["multiplier"] > 1:
                txt, col = f"SPEED BOOST: {rem:.1f}s", CYAN
            else:
                txt, col = f"SLOW MOTION: {rem:.1f}s", BLUE
            self.screen.blit(font.render(txt, True, col), (10, y_off))

        pygame.display.flip()

  
    # Main run loop


    def run(self):
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if   event.key == pygame.K_UP    and self.snake.direction != DOWN:
                        self.snake.direction = UP
                    elif event.key == pygame.K_DOWN  and self.snake.direction != UP:
                        self.snake.direction = DOWN
                    elif event.key == pygame.K_LEFT  and self.snake.direction != RIGHT:
                        self.snake.direction = LEFT
                    elif event.key == pygame.K_RIGHT and self.snake.direction != LEFT:
                        self.snake.direction = RIGHT

            self.update()
            self.draw()
            self.clock.tick(self.get_speed())

        return True