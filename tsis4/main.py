    

import pygame
import sys
import random
from datetime import datetime
from config import *
from game import Game
from db import Database
from settings_manager import SettingsManager


class Button:
    """Creates clickable UI buttons"""
    
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.font = pygame.font.Font(None, 36)
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.current_color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            return True
        self.current_color = self.color
        return False
    
    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click


class TextInput:
    """Handles keyboard input for username entry"""
    
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.active = False
        self.font = pygame.font.Font(None, 36)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(self.text) < 20:
                    self.text += event.unicode
        return False
    
    def draw(self, screen):
        bg_color = (100, 100, 100) if self.active else (50, 50, 50)
        pygame.draw.rect(screen, bg_color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        display_text = self.text if self.text else "Enter username"
        text_color = WHITE if self.text else (100, 100, 100)
        text_surface = self.font.render(display_text, True, text_color)
        screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))


class GameApp:
    """Manages all game screens and application flow"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_screen = "menu"
        self.username = None
        self.settings_manager = SettingsManager()
        
        # Try to connect to database, but don't fail if not available
        try:
            self.db = Database()
            self.use_database = True
            print("Database connected successfully!")
        except Exception as e:
            print(f"Database not available: {e}")
            print("Using local leaderboard data instead.")
            self.db = None
            self.use_database = False
        
        # Game stats
        self.final_score = 0
        self.final_level = 0
        
        # Buttons
        self.play_btn = None
        self.leaderboard_btn = None
        self.settings_btn = None
        self.quit_btn = None
        self.retry_btn = None
        self.menu_btn = None
        self.back_btn = None
        self.save_btn = None
        self.username_input = None
        
        # SAMPLE LEADERBOARD DATA (for testing without database)
        self.leaderboard_data = self.get_sample_leaderboard_data()
        
        # Track player's scores (for database mode)
        self.player_scores = []
    
    def get_sample_leaderboard_data(self):
        """
        Generates sample leaderboard data for testing
        This ensures leaderboard always shows data even without database
        """
        sample_data = [
            ("🏆 MASTER", 999, 20, "2026-04-27 23:59"),
            ("SNAKE_KING", 850, 17, "2026-04-27 22:30"),
            ("PythonPro", 720, 15, "2026-04-27 20:15"),
            ("GameMaster", 645, 13, "2026-04-27 18:45"),
            ("SpeedDemon", 580, 12, "2026-04-27 16:20"),
            ("WallHacker", 510, 11, "2026-04-27 14:00"),
            ("FoodLover", 450, 10, "2026-04-26 22:30"),
            ("ShieldKing", 390, 9, "2026-04-26 20:00"),
            ("BoostMaster", 340, 8, "2026-04-26 17:45"),
            ("SlowMotion", 290, 7, "2026-04-26 15:30"),
            ("NewbieOne", 150, 4, "2026-04-26 12:00"),
            ("NewbieTwo", 100, 3, "2026-04-25 23:00"),
            ("JustStarted", 50, 2, "2026-04-25 20:00"),
            ("FirstTry", 25, 1, "2026-04-25 18:30"),
        ]
        return sample_data
    
    def refresh_leaderboard(self):
        """Refresh leaderboard data from database or use sample data"""
        if self.use_database and self.db:
            try:
                db_data = self.db.get_leaderboard(10)
                if db_data and len(db_data) > 0:
                    self.leaderboard_data = db_data
                    print(f"Loaded {len(db_data)} scores from database")
                else:
                    print("No data in database, using sample data")
                    # Keep sample data if database is empty
                    pass
            except Exception as e:
                print(f"Error loading from database: {e}")
                # Keep sample data
        else:
            # If we have player scores, add them to sample data for display
            if self.player_scores:
                # Combine sample data with player scores and sort
                all_scores = list(self.leaderboard_data) + self.player_scores
                # Sort by score (descending)
                all_scores.sort(key=lambda x: x[1], reverse=True)
                self.leaderboard_data = all_scores[:10]  # Keep top 10
                print(f"Using combined data: {len(self.leaderboard_data)} entries")
    
    def add_score_to_leaderboard(self, username, score, level):
        """Add a new score to the local leaderboard"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_entry = (username, score, level, current_time)
        
        # Add to player scores list
        self.player_scores.append(new_entry)
        
        # Combine with sample data and sort
        all_scores = list(self.leaderboard_data) + self.player_scores
        # Remove duplicates (keep highest score per player)
        unique_scores = {}
        for entry in all_scores:
            name = entry[0]
            if name not in unique_scores or entry[1] > unique_scores[name][1]:
                unique_scores[name] = entry
        
        # Convert back to list and sort
        all_scores = list(unique_scores.values())
        all_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Keep top 15 for display
        self.leaderboard_data = all_scores[:15]
        print(f"Added score: {username} - {score} points (Level {level})")
        print(f"Leaderboard now has {len(self.leaderboard_data)} entries")
    
    def start_game(self):
        """Starts a new game session"""
        game = Game(self.username, self.settings_manager)
        game.run()
        self.current_screen = "game_over"
        self.final_score = game.score
        self.final_level = game.level
        
        # Add score to leaderboard
        self.add_score_to_leaderboard(self.username, self.final_score, self.final_level)
        
        # Save to database if available
        if self.use_database and self.db:
            try:
                self.db.save_game_result(self.username, self.final_score, self.final_level)
                print("Score saved to database")
            except Exception as e:
                print(f"Could not save to database: {e}")
    
    def draw_menu(self):
        """Draws the main menu screen"""
        self.screen.fill(BLACK)
        
        # Title
        font = pygame.font.Font(None, 72)
        title = font.render("SNAKE GAME", True, GREEN)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        font_small = pygame.font.Font(None, 24)
        subtitle = font_small.render("Eat food, avoid walls, collect power-ups!", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 160))
        self.screen.blit(subtitle, subtitle_rect)
        
        if not self.username:
            # Username entry mode
            prompt = pygame.font.Font(None, 36).render("Enter your username:", True, WHITE)
            prompt_rect = prompt.get_rect(center=(WINDOW_WIDTH // 2, 240))
            self.screen.blit(prompt, prompt_rect)
            
            if self.username_input is None:
                self.username_input = TextInput(WINDOW_WIDTH // 2 - 150, 280, 300, 50)
            self.username_input.draw(self.screen)
            
            if self.username_input.text:
                info_font = pygame.font.Font(None, 24)
                info = info_font.render("Press ENTER to continue", True, (100, 100, 100))
                info_rect = info.get_rect(center=(WINDOW_WIDTH // 2, 360))
                self.screen.blit(info, info_rect)
            
            # Show that sample leaderboard is available
            sample_note = font_small.render("(Sample leaderboard data loaded for demo)", True, (100, 100, 100))
            sample_rect = sample_note.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
            self.screen.blit(sample_note, sample_rect)
        else:
            # Main menu buttons
            if self.play_btn is None:
                self.play_btn = Button(WINDOW_WIDTH // 2 - 100, 240, 200, 50, "PLAY", (0, 100, 0), (0, 200, 0))
                self.leaderboard_btn = Button(WINDOW_WIDTH // 2 - 100, 310, 200, 50, "LEADERBOARD", (0, 0, 100), (0, 0, 200))
                self.settings_btn = Button(WINDOW_WIDTH // 2 - 100, 380, 200, 50, "SETTINGS", (100, 100, 0), (200, 200, 0))
                self.quit_btn = Button(WINDOW_WIDTH // 2 - 100, 450, 200, 50, "QUIT", (100, 0, 0), (200, 0, 0))
            
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()[0]
            
            self.play_btn.update(mouse_pos)
            self.leaderboard_btn.update(mouse_pos)
            self.settings_btn.update(mouse_pos)
            self.quit_btn.update(mouse_pos)
            
            self.play_btn.draw(self.screen)
            self.leaderboard_btn.draw(self.screen)
            self.settings_btn.draw(self.screen)
            self.quit_btn.draw(self.screen)
            
            # Show player info
            info_font = pygame.font.Font(None, 24)
            username_text = info_font.render(f"Player: {self.username}", True, WHITE)
            
            # Get personal best (try database first, then local)
            personal_best = 0
            if self.use_database and self.db:
                try:
                    personal_best = self.db.get_personal_best(self.username)
                except:
                    personal_best = 0
            
            # Also check local scores
            for entry in self.leaderboard_data:
                if entry[0] == self.username and entry[1] > personal_best:
                    personal_best = entry[1]
            
            best_text = info_font.render(f"Personal Best: {personal_best}", True, YELLOW)
            self.screen.blit(username_text, (10, WINDOW_HEIGHT - 40))
            self.screen.blit(best_text, (10, WINDOW_HEIGHT - 20))
            
            # Handle clicks
            if self.play_btn.is_clicked(mouse_pos, mouse_click):
                self.start_game()
            elif self.leaderboard_btn.is_clicked(mouse_pos, mouse_click):
                self.current_screen = "leaderboard"
                self.refresh_leaderboard()
            elif self.settings_btn.is_clicked(mouse_pos, mouse_click):
                self.current_screen = "settings"
            elif self.quit_btn.is_clicked(mouse_pos, mouse_click):
                self.running = False
    
    def draw_game_over(self):
        """Draws the game over screen"""
        self.screen.fill(BLACK)
        
        font_big = pygame.font.Font(None, 72)
        game_over_text = font_big.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(game_over_text, text_rect)
        
        # Get personal best
        personal_best = 0
        for entry in self.leaderboard_data:
            if entry[0] == self.username and entry[1] > personal_best:
                personal_best = entry[1]
        
        font_med = pygame.font.Font(None, 48)
        score_text = font_med.render(f"Score: {self.final_score}", True, WHITE)
        level_text = font_med.render(f"Level: {self.final_level}", True, WHITE)
        best_text = font_med.render(f"Personal Best: {personal_best}", True, YELLOW)
        
        # Check if new record
        if self.final_score > personal_best and personal_best > 0:
            new_record = font_med.render("NEW RECORD!", True, GREEN)
            new_record_rect = new_record.get_rect(center=(WINDOW_WIDTH // 2, 360))
            self.screen.blit(new_record, new_record_rect)
            score_y = 200
            level_y = 260
            best_y = 320
        else:
            score_y = 200
            level_y = 260
            best_y = 320
        
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, score_y))
        level_rect = level_text.get_rect(center=(WINDOW_WIDTH // 2, level_y))
        best_rect = best_text.get_rect(center=(WINDOW_WIDTH // 2, best_y))
        
        self.screen.blit(score_text, score_rect)
        self.screen.blit(level_text, level_rect)
        self.screen.blit(best_text, best_rect)
        
        if self.retry_btn is None:
            self.retry_btn = Button(WINDOW_WIDTH // 2 - 120, 420, 100, 50, "RETRY", (0, 100, 0), (0, 200, 0))
            self.menu_btn = Button(WINDOW_WIDTH // 2 + 20, 420, 100, 50, "MENU", (100, 0, 0), (200, 0, 0))
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        
        self.retry_btn.update(mouse_pos)
        self.menu_btn.update(mouse_pos)
        
        self.retry_btn.draw(self.screen)
        self.menu_btn.draw(self.screen)
        
        if self.retry_btn.is_clicked(mouse_pos, mouse_click):
            self.start_game()
        elif self.menu_btn.is_clicked(mouse_pos, mouse_click):
            self.current_screen = "menu"
    
    def draw_leaderboard(self):
        """Draws the leaderboard screen showing top scores"""
        self.screen.fill(BLACK)
        
        # Title
        font_big = pygame.font.Font(None, 72)
        title = font_big.render("LEADERBOARD", True, YELLOW)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Show data source info
        font_small = pygame.font.Font(None, 20)
        if self.use_database:
            info_text = "Data source: PostgreSQL Database"
        else:
            info_text = "Data source: Sample Data (Database not connected)"
        info_surface = font_small.render(info_text, True, (100, 100, 100))
        info_rect = info_surface.get_rect(center=(WINDOW_WIDTH // 2, 90))
        self.screen.blit(info_surface, info_rect)
        
        # Get data
        if not self.leaderboard_data:
            self.refresh_leaderboard()
        
        if not self.leaderboard_data:
            # No data message
            font = pygame.font.Font(None, 48)
            no_scores = font.render("No scores yet! Play a game!", True, WHITE)
            no_rect = no_scores.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(no_scores, no_rect)
        else:
            # Headers
            font = pygame.font.Font(None, 32)
            headers = ["Rank", "Username", "Score", "Level", "Date"]
            header_x = [60, 180, 400, 500, 580]
            
            for i, header in enumerate(headers):
                header_text = font.render(header, True, WHITE)
                self.screen.blit(header_text, (header_x[i], 130))
            
            # Draw horizontal line
            pygame.draw.line(self.screen, WHITE, (40, 160), (WINDOW_WIDTH - 40, 160), 2)
            
            # Display each row
            y_offset = 180
            for i, entry in enumerate(self.leaderboard_data[:15]):  # Show top 15
                # Handle different data formats
                if len(entry) == 4:
                    username, score, level, played_at = entry
                else:
                    continue
                
                rank = i + 1
                
                # Color for top 3
                if rank == 1:
                    rank_color = (255, 215, 0)  # Gold
                    bg_color = (255, 215, 0, 30)  # Gold tint
                elif rank == 2:
                    rank_color = (192, 192, 192)  # Silver
                    bg_color = (192, 192, 192, 30)
                elif rank == 3:
                    rank_color = (205, 127, 50)  # Bronze
                    bg_color = (205, 127, 50, 30)
                else:
                    rank_color = WHITE
                    bg_color = None
                
                # Highlight current player's row
                if username == self.username:
                    # Draw highlight background
                    highlight_rect = pygame.Rect(30, y_offset - 5, WINDOW_WIDTH - 60, 35)
                    pygame.draw.rect(self.screen, (0, 100, 0), highlight_rect)
                
                # Draw rank with medal emoji for top 3
                if rank == 1:
                    rank_display = "🥇 1"
                elif rank == 2:
                    rank_display = "🥈 2"
                elif rank == 3:
                    rank_display = "🥉 3"
                else:
                    rank_display = str(rank)
                
                rank_text = font.render(rank_display, True, rank_color)
                name_text = font.render(username[:15], True, WHITE)
                score_text = font.render(str(score), True, GREEN if rank <= 3 else WHITE)
                level_text = font.render(str(level), True, WHITE)
                date_text = font.render(played_at[:10] if len(played_at) > 10 else played_at, True, (150, 150, 150))
                
                self.screen.blit(rank_text, (header_x[0], y_offset))
                self.screen.blit(name_text, (header_x[1], y_offset))
                self.screen.blit(score_text, (header_x[2], y_offset))
                self.screen.blit(level_text, (header_x[3], y_offset))
                self.screen.blit(date_text, (header_x[4], y_offset))
                
                y_offset += 40
                if y_offset > WINDOW_HEIGHT - 100:
                    break
        
        # Back button
        if self.back_btn is None:
            self.back_btn = Button(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT - 70, 100, 40, "BACK", (50, 50, 50), (100, 100, 100))
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        
        self.back_btn.update(mouse_pos)
        self.back_btn.draw(self.screen)
        
        # Show instructions
        inst_font = pygame.font.Font(None, 20)
        inst_text = inst_font.render("Press ESC or click BACK to return to menu", True, (100, 100, 100))
        inst_rect = inst_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 25))
        self.screen.blit(inst_text, inst_rect)
        
        if self.back_btn.is_clicked(mouse_pos, mouse_click):
            self.current_screen = "menu"
    
    def draw_settings(self):
        """Draws the settings screen"""
        self.screen.fill(BLACK)
        
        font_big = pygame.font.Font(None, 72)
        title = font_big.render("SETTINGS", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)
        
        font = pygame.font.Font(None, 36)
        y_offset = 150
        
        # Grid toggle
        grid_status = "ON" if self.settings_manager.get("grid_overlay") else "OFF"
        grid_text = font.render(f"☐ Grid Overlay: {grid_status}", True, WHITE)
        grid_rect = grid_text.get_rect(topleft=(100, y_offset))
        self.screen.blit(grid_text, grid_rect)
        
        # Sound toggle (placeholder for future)
        sound_status = "ON" if self.settings_manager.get("sound_enabled") else "OFF"
        sound_text = font.render(f"🔊 Sound: {sound_status}", True, WHITE)
        sound_rect = sound_text.get_rect(topleft=(100, y_offset + 50))
        self.screen.blit(sound_text, sound_rect)
        
        # Snake color
        color_text = font.render("🐍 Snake Color:", True, WHITE)
        self.screen.blit(color_text, (100, y_offset + 100))
        
        snake_color = tuple(self.settings_manager.get("snake_color"))
        color_preview = pygame.Rect(320, y_offset + 95, 40, 30)
        pygame.draw.rect(self.screen, snake_color, color_preview)
        pygame.draw.rect(self.screen, WHITE, color_preview, 2)
        
        colors = [
            (GREEN, "Green"), (RED, "Red"), (BLUE, "Blue"),
            (YELLOW, "Yellow"), (PURPLE, "Purple"), (ORANGE, "Orange")
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        
        for i, (color, name) in enumerate(colors):
            btn_rect = pygame.Rect(380 + i * 70, y_offset + 95, 60, 30)
            pygame.draw.rect(self.screen, color, btn_rect)
            pygame.draw.rect(self.screen, WHITE, btn_rect, 2)
            
            if btn_rect.collidepoint(mouse_pos) and mouse_click:
                self.settings_manager.set("snake_color", list(color))
                pygame.time.wait(150)
        
        # Handle toggles
        if grid_rect.collidepoint(mouse_pos) and mouse_click:
            self.settings_manager.set("grid_overlay", not self.settings_manager.get("grid_overlay"))
            pygame.time.wait(200)
        
        if sound_rect.collidepoint(mouse_pos) and mouse_click:
            self.settings_manager.set("sound_enabled", not self.settings_manager.get("sound_enabled"))
            pygame.time.wait(200)
        
        # Back button
        back_text = font.render("Press ESC to go back", True, (100, 100, 100))
        back_rect = back_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 40))
        self.screen.blit(back_text, back_rect)
    
    def run(self):
        """Main application loop"""
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()[0]
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.current_screen == "settings":
                            self.current_screen = "menu"
                        elif self.current_screen == "leaderboard":
                            self.current_screen = "menu"
                
                # Handle username input
                if self.current_screen == "menu" and self.username is None:
                    if self.username_input is None:
                        self.username_input = TextInput(WINDOW_WIDTH // 2 - 150, 280, 300, 50)
                    if self.username_input.handle_event(event):
                        self.username = self.username_input.text
            
            # Draw current screen
            if self.current_screen == "menu":
                self.draw_menu()
            elif self.current_screen == "game_over":
                self.draw_game_over()
            elif self.current_screen == "leaderboard":
                self.draw_leaderboard()
            elif self.current_screen == "settings":
                self.draw_settings()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        # Cleanup
        if self.use_database and self.db:
            self.db.close()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    print("=" * 50)
    print("SNAKE GAME STARTING")
    print("=" * 50)
    print("\nLeaderboard includes sample data for testing!")
    print("Your scores will be added to the leaderboard during gameplay.")
    print("\nControls:")
    print("  Arrow Keys - Move snake")
    print("  ESC - Go back in menus")
    print("=" * 50 + "\n")
    
    app = GameApp()
    app.run()