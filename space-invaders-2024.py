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
import math
import random
import itertools
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
        speed = 135
        angle_r = angle_d * np.pi / 180
        self.t = 0
        self.dt = 0.1
        self.x = x
        self.y = y
        self.vx = speed * np.cos(angle_r)
        self.vy = speed * np.sin(angle_r)
        self.colour = colour
        self.gamma = 0.0001
        self.g = 1.62 #moon
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
        pygame.draw.circle(surface=screen, color=self.colour, center=(self.x, self.y), radius=5)

#This class draws a line that comes out of the player sprite
#You can change the angle of this line with the arrow keys to aim your shots
class Aim:
    def __init__(self, x, y, angle, colour):
        self.x = x
        self.y = y
        self.angle = angle
        self.colour = colour
        pass
    
    def update(self, x, angle):
        self.x = x
        self.angle = angle
    
    def draw(self, screen):

        end_x = self.x - math.cos(math.radians(self.angle)) * 20
        end_y = self.y - math.sin(math.radians(self.angle)) * 20

        pygame.draw.line(screen, self.colour, (self.x, self.y), (end_x, end_y), width=4)

class Invader:
    def __init__(self, x, y, imagefile):
        #self.x = x
        #self.y = y
        self.image = load_image(imagefile)
        #this rectangle is at the same position as the invader sprite
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        
    def update(self, x, y):
        self.rect.x = x
        self.rect.y = y

        
    def draw(self, screen):
        screen.blit(self.image, self.rect)
    
class Invader:
    def __init__(self, x, y, imagefile):
        #self.x = x
        #self.y = y
        self.image = load_image(imagefile)
        #this rectangle is at the same position as the invader sprite
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, x, y):
        self.rect.x = x
        self.rect.y = y

        
    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Barrier:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        
    def update(self, x, y):
        self.x = x
        self.y = y

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, Rect(self.x, self.y, self.width, self.height),
                         width=0, border_radius=10)

def main():
    pygame.init()
    pygame.font.init()
    
    siFont = pygame.font.SysFont("agencyfb", 30)
    
    fps = 30
    fpsClock = pygame.time.Clock()
    
    width, height = 640, 640
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Space Invaders 2024')
    
    #INIT for Objects
    objs = []
    objs.append((Player(288, 550, 'resources/player.png')))
    objs.append((Aim(objs[0].rect.centerx, objs[0].rect.centery-10, 90, RED)))
    
    barr_objs = []
    barr_objs.append(Barrier(450, 450, 100, 75))
    barr_objs.append(Barrier(90, 450, 100, 75))
    barr_objs.append(Barrier(295, 450, 50, 75))

    #INIT for invaders
    #Since there are so many invaders and they function very differently from the objects in the above objs I decided to make a
    #new enemy_objs to hold the invaders. Feel free to change this if you think it would be better another way
    enemy_objs = []
    pos_x = 10
    pos_y = 10

    #place the enemies in a grid formation
    while pos_y <= 220:
        if pos_x < 570:
            enemy_objs.append((Invader(pos_x, pos_y, 'resources/enemy1.png')))
            pos_x += 80
        else:
            pos_x = 10
            pos_y += 70
        
            
    #the enemies move once every timed interval. These variables allow the timer to function
    last_print_time = pygame.time.get_ticks()
    print_interval = 1500 #timed interval in ms

    # 0 - up, 1 - left, 2 - down, 3 - right
    enemy_walk = 2 
    
    #game over hasnt been met
    game_run = True
    
    # Game loop.
    while game_run:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        
        # Update
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            objs[0].update(objs[0].rect.x - 10)
            objs[1].update(objs[1].x - 10, objs[1].angle)
        if keys[pygame.K_d]:
            objs[0].update(objs[0].rect.x + 10)
            objs[1].update(objs[1].x + 10, objs[1].angle)

        #aim shot
        if keys[pygame.K_LEFT]:
            if objs[1].angle > 0:
                objs[1].update(objs[1].x, objs[1].angle - 5)
        if keys[pygame.K_RIGHT]:
            if objs[1].angle < 180:
                objs[1].update(objs[1].x, objs[1].angle + 5)
            
        #shoot
        if keys[pygame.K_UP] or keys[pygame.K_SPACE] or keys[pygame.K_w]:
            if len(objs) == 2:
                objs.append((Projectile(objs[0].rect.centerx, objs[0].rect.centery, objs[1].angle, RED)))
        
        #3 second timer loop for enemy movement
        current_time = pygame.time.get_ticks()
        if current_time - last_print_time >= print_interval:
            # 0 - up, 1 - right, 2 - down, 3 - left
            enemy_walk = random.choices(range(0,4), [5/100, 30/100, 35/100, 30/100])[0] #weighted random
            #if enemy_right true then move right every 3 seconds
            for invader in enemy_objs:    
                # 0 - up, 1 - right, 2 - down, 3 - left
                if invader.rect.x >= 560:
                    #move all invaders down by 5
                    for invader in enemy_objs:    
                        invader.rect.y += 5
                    #set enemies to move left
                    enemy_walk = 3
                elif invader.rect.x <= 10:
                    for invader in enemy_objs:    
                        invader.rect.y += 5
                    #set enemies to move right
                    enemy_walk = 1
                if invader.rect.y <= 10:
                    for invader in enemy_objs:    
                        invader.rect.y += 10 
                
            for invader in enemy_objs:        
                # 0 - up, 1 - right, 2 - down, 3 - left
                if enemy_walk == 0:
                    invader.update(invader.rect.x, invader.rect.y - 10)
                elif enemy_walk == 1:
                    invader.update(invader.rect.x + 15, invader.rect.y)
                elif enemy_walk == 2:
                    invader.update(invader.rect.x, invader.rect.y + 15)
                elif enemy_walk == 3:
                    invader.update(invader.rect.x - 15, invader.rect.y)
                    
            #timer loop over
            last_print_time = current_time
        
        #projectile collision detection
        for i in objs[2:]:
            #projectile - enemy
            for j in enemy_objs:
                if i.x < j.rect.x + 64 and i.x > j.rect.x and i.y < j.rect.y + 64 and i.y > j.rect.y:
                    objs.remove(i)
                    enemy_objs.remove(j)
            #projectile - barrier
            for j in barr_objs:
                if i.x < j.x + j.width and i.x > j.x and i.y < j.y + j.height and i.y > j.y:
                    objs.remove(i)
            #projectile boundry check - if outside box remove projectile else update it
            if i.x > width or i.x < 0 or i.y > height or i.y < -height:
                objs.remove(i)
            else:
                i.update()
                
       
        for i in enemy_objs:
            for j in barr_objs:
                #checks if feet are in the barrier 
                if (i.rect.y + 64 > j.y 
                    and ((i.rect.x > j.x and i.rect.x < j.x + j.width) 
                    or (i.rect.x + 64 > j.x and i.rect.x + 64 < j.x + j.width))):
                    enemy_objs.remove(i)
                    barr_objs.remove(j)
                    
       # if an enemy reaches the player ends game
        for i in enemy_objs:
            if i.rect.y + 32 > objs[0].y:
                game_run = False
        #if there are less than half enemies speed up
        if len(enemy_objs) < 14:
            print_interval = 1000
        #if there are less than quater enemies speed up
        if len(enemy_objs) < 7:
            print_interval = 500
        #if there are no remaining enemies
        if not enemy_objs:
            game_run = False
       
        # Draw
        for i in enemy_objs:
            i.draw(screen)
        for i in objs:
            i.draw(screen)
        for i in barr_objs:
            i.draw(screen)
        
        
        pygame.display.flip()
        fpsClock.tick(fps)
        
    
    #GAME OVER STUFF
    screen.fill(BLACK)
    g_o = siFont.render("GAME OVER", True, WHITE)
    #if there are no remaining enemies 
    if not enemy_objs:
        y_w = siFont.render("YOU WIN", True, WHITE)
        screen.blit(y_w, (277,340))
    else:
        y_l = siFont.render("YOU LOSE", True, WHITE)
        screen.blit(y_l, (277,340))
    screen.blit(g_o, (265,300))
    pygame.display.flip()
    
    #waits for key press
    pygame.event.clear()
    while True:
        event = pygame.event.wait()
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            break
         
        
        
if __name__ == '__main__':
    main()
