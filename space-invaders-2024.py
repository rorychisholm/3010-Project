"""
May Robertson - 100751769
William Rory Chisholm - 100560820

~ Space Invaders 2024 ~
3010U - Simulation and Modling Project

April 5th, 2024
"""

import sys
 
import pygame
from pygame.locals import *

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class Player:
    def __init__(self, x, y, colour):
        self.x = x
        self.y = y
        self.colour = colour
        pass
        
    def update(self, x):
        self.x = x
        
    def draw(self, screen):
        pygame.draw.polygon(screen, self.colour, ((self.x-15, self.y+15), 
                                                    (self.x, self.y-15),
                                                    (self.x+15, self.y+15)))
    
class Invader:
    def __init__(self, x, y, colour):
        self.x = x
        self.y = y
        self.colour = colour
        pass
        
    def update(self):
        pass
        
    def draw(self, screen):
        pass

class Sim:
    def __init__(self):
        pass
 
def main():
    pygame.init()
    
    fps = 60
    fpsClock = pygame.time.Clock()
    
    width, height = 640, 640
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Space Invaders 2024')
    
    objs = []
    objs.append((Player(0, 600, WHITE)))
    
    # Game loop.
    while True:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        
        # Update.
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                objs[0].update(objs[0].x - 10)
            if event.key == pygame.K_RIGHT:
                objs[0].update(objs[0].x + 10)
                
        # Draw.
        for i in objs:
            i.draw(screen)
        
        pygame.display.flip()
        fpsClock.tick(fps)
    
    
if __name__ == '__main__':
    main()
