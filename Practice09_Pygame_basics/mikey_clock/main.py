
import pygame
from clock import MickeyClock 

def main():
    pygame.init()
    
    try:
        mickey_clock = MickeyClock()
        mickey_clock.run()
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()