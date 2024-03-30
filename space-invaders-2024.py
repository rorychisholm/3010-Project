"""
May Robertson - 100751769
William Rory Chisholm - 100560820

~ Space Invaders 2024 ~
3010U - Simulation and Modling Project

April 5th, 2024
"""

import sys
import numpy as np
import pygame
from pygame.locals import *

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

#used to get load files
def load_image(name):
    image = pygame.image.load(name)
    return image

#Player Class for our little shooting hero controls movement for now
class Player:
    def __init__(self, x, y, imagefile):
        self.x = x
        self.y = y
        self.image = load_image(imagefile)
        #this rectangle is at the same position as the player sprite
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        pass
        
    def update(self, x):
        self.rect.x = x
        
    def draw(self, screen):
        screen.blit(self.image, self.rect)

    
class Projectile:
    def __init__(self, x, y, angle_d, colour):
        speed = 110
        angle_r = angle_d * np.pi / 180
        self.t = 0
        self.dt = 1
        self.x = x
        self.y = y
        self.vx = speed * np.cos(angle_r)
        self.vy = speed * np.sin(angle_r)
        self.colour = colour
        self.gamma = 0.0001
        self.g = 9.8
        pass

    def update(self):
        self.t += self.dt
        dx = self.vx * self.dt
        dy = self.vy * self.dt
        dvx = -(self.gamma * self.vx)
        dvy = -(self.g + self.gamma * self.vy)
        
        self.x -= dx
        self.y -= dy
        self.vx += dvx
        self.vy += dvy
        
       
    
    def draw(self, screen):
        #print(self.x)
        pygame.draw.circle(surface=screen, color=self.colour, center=(self.x, self.y), radius=5)
    
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
    
    fps = 30
    fpsClock = pygame.time.Clock()
    
    width, height = 640, 640
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Space Invaders 2024')
    
    #INIT for Objects
    objs = []
    objs.append((Player(0, 550, 'resources/player.png')))
    
    # Game loop.
    while True:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        
        # Update
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            objs[0].update(objs[0].rect.x - 10)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            objs[0].update(objs[0].rect.x + 10)
        if keys[pygame.K_UP] or keys[pygame.K_SPACE] or keys[pygame.K_w]:
            objs.append((Projectile(objs[0].x, objs[0].y, 90, RED)))


        for i in objs[1:]:
            if i.x > width or i.x < 0 or i.y > height or i.y < -height:
                objs.remove(i)
            else:
                i.update()
        # Draw
        for i in objs:
            i.draw(screen)
        
        pygame.display.flip()
        fpsClock.tick(fps)
    
    
if __name__ == '__main__':
    main()
