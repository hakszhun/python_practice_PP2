import pygame
import datetime
import math

class MickeyClock:
    def __init__(self):

        self.WIDTH, self.HEIGHT = 600, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("часики")
        
        self.center_x = self.WIDTH // 2
        self.center_y = self.HEIGHT // 2
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (0, 0, 255)
        self.RED = (255, 0, 0)
        self.circle_radius = 250
        
    def draw_hand(self, color, length, width, angle):

        end_x = self.center_x + length * math.cos(math.radians(90 - angle))
        end_y = self.center_y - length * math.sin(math.radians(90 - angle))
        pygame.draw.line(self.screen, color, (self.center_x, self.center_y), 
                        (end_x, end_y), width)
        pygame.draw.circle(self.screen, color, (int(end_x), int(end_y)), width // 2)
    
    def draw_numbers(self):
        font = pygame.font.Font(None, 45)
        
        for hour in range(1, 13):
            angle = 90 - (hour * 30)
            angle_rad = math.radians(angle)
            
            number_radius = self.circle_radius - 35
            x = self.center_x + number_radius * math.cos(angle_rad)
            y = self.center_y - number_radius * math.sin(angle_rad)
            
            text = font.render(str(hour), True, self.BLACK)
            text_rect = text.get_rect(center=(x, y))
            self.screen.blit(text, text_rect)
    
    def draw_clock_face(self):
        pygame.draw.circle(self.screen, self.BLACK, (self.center_x, self.center_y), 
                          self.circle_radius, 8)
        pygame.draw.circle(self.screen, self.BLACK, (self.center_x, self.center_y), 8)
        self.draw_numbers()
    
    def calculate_angles(self):
        now = datetime.datetime.now()
        
        seconds = now.second + now.microsecond / 1000000.0
        second_angle = seconds * 6
        
        minutes = now.minute + now.second / 60.0
        minute_angle = minutes * 6
        
        return minute_angle, second_angle
    
    def update_display(self):
        minute_angle, second_angle = self.calculate_angles()
        
        self.screen.fill(self.WHITE)
        
  
        self.draw_clock_face()
        
    
        self.draw_hand(self.RED, 220, 3, second_angle)   
        self.draw_hand(self.BLUE, 180, 8, minute_angle) 
        
        pygame.display.flip()
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            self.update_display()
            clock.tick(60)  
        
        pygame.quit()