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
from scipy.integrate import ode

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
    def __init__(self, x, y, exploded, imagefile):
        self.image = load_image(imagefile)
        self.image_rot = self.image

        #this rectangle is at the same position as the invader sprite
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.exploded = False
        
        
        self.vy = 0 #initialize y velocity to 0
        self.m = 5.0
        self.g = 1.62 #moon
        
    def rotate(self, angle):
        self.image_rot = pygame.transform.rotate(self.image, angle)

        
    def shot(self):
        self.exploded = True
        
    def update(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def draw(self, screen):
        rect = self.image_rot.get_rect()
        rect.center = (self.rect.x, self.rect.y)
        rect.centery = rect.centery 
        screen.blit(self.image_rot, self.rect)
        #screen.blit(self.image, self.rect)
        #pygame.draw.rect(screen, RED, self.rect, 1)
        

    def fall(self, y):
        self.rect.y = y
        # Calculate the force using F = mass * gravity
        f = self.m * self.g
        # Acceleration is force divided by mass
        a = f / self.m
        # Update vertical velocity using acceleration
        self.vy += a
        # Update y position based on vertical velocity
        self.rect.y = y + self.vy
    


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


class RigidBody:

    def __init__(self, force, torque):
        self.mass = 1.0                       # mass
        self.Ibody = np.identity(3)           # inertia tensor
        self.IbodyInv = np.linalg.inv(self.Ibody)  # inverse of inertia tensor
        self.v = np.zeros(3)       # linear velocity
        self.omega = np.zeros(3)   # angular velocity

        self.state = np.zeros(19)
        self.state[0:3] = np.zeros(3)                     # position
        self.state[3:12] = np.identity(3).reshape([1,9])  # rotation
        self.state[12:15] = self.mass * self.v            # linear momentum
        self.state[15:18] = np.zeros(3)                   # angular momentum

        # Computed quantities
        self.force = force
        self.torque = torque

        # Setting up the solver
        self.solver = ode(self.f)
        self.solver.set_integrator('dop853')
        self.solver.set_f_params(self.force, self.torque, self.IbodyInv)

    def f(self, t, state, force, torque, IbodyInv):
        rate = np.zeros(19)
        rate[0:3] = state[12:15] / self.mass  # dv = dx/dt

        _R = state[3:12].reshape([3,3])
        _R = self.orthonormalize(_R)
        Iinv = np.dot(_R, np.dot(IbodyInv, _R.T))
        _L = state[15:18]
        omega = np.dot(Iinv, _L)

        rate[3:12] = np.dot(self.star(omega), _R).reshape([1,9])
        rate[12:15] = force
        rate[15:18] = torque
        return rate

    def star(self, v):
        vs = np.zeros([3,3])
        vs[0][0] = 0
        vs[1][0] = v[2]
        vs[2][0] = -v[1]
        vs[0][1] = -v[2]
        vs[1][1] = 0
        vs[2][1] = v[0]
        vs[0][2] = v[1] 
        vs[1][2] = -v[0]
        vs[2][2] = 0
        return vs;       

    def orthonormalize(self, m):
        mo = np.zeros([3,3])
        r0 = m[0,:]
        r1 = m[1,:]
        r2 = m[2,:]
        
        r0new = r0 / np.linalg.norm(r0)
        
        r2new = np.cross(r0new, r1)
        r2new = r2new / np.linalg.norm(r2new)

        r1new = np.cross(r2new, r0new)
        r1new = r1new / np.linalg.norm(r1new)

        mo[0,:] = r0new
        mo[1,:] = r1new
        mo[2,:] = r2new
        return mo

    def get_pos(self):
        return self.state[0:3]

    def get_rot(self):
        return self.state[3:12].reshape([3,3])

    def get_angle_2d(self):
        v1 = [1,0,0]
        v2 = np.dot(self.state[3:12].reshape([3,3]), v1)
        #print(v1, v2)

        cosang = np.dot(v1, v2)
        axis = np.cross(v1, v2)
        return np.degrees(np.arccos(cosang)), axis

    def prn_state(self):
        print('Pos', self.state[0:3])
        print('Rot', self.state[3:12].reshape([3,3]))
        print('P', self.state[12:15])
        print('L', self.state[15:18])


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

    '''
    INIT for invaders
    Initialization for the list that will hold all Invader objects
    '''
    enemy_objs = []
    pos_x = 10
    pos_y = 10

    exploded_enemy_objs = []

    '''
    INIT for rigid body class. This will handle all the physics involved in any rigid 
    body simulation in the program.
    '''
    rb = RigidBody([0,-1,0], [0,0,0.1])
    cur_time = 0.0
    dt = 0.1

    rb.solver.set_initial_value(rb.state, cur_time)

    

    #place the enemies in a grid formation
    while pos_y <= 220:
        if pos_x < 570:
            enemy_objs.append((Invader(pos_x, pos_y, False, 'resources/enemy1.png')))
            exploded_enemy_objs.append((Invader(pos_x, pos_y, False, 'resources/explosion.png')))
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
                if not invader.exploded:
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
                    #Enemy falls and rotates with rigid body physics simulation
                    objs.remove(i)
                    j.shot()
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
            if (i.rect.y + 32 > objs[0].y) and (i.rect.x < objs[0].rect.x + objs[0].rect.width and i.rect.x + i.rect.width > objs[0].rect.x):
                game_run = False
            if i.exploded:
                rb.state = rb.solver.integrate(cur_time)
                cur_time += dt
                #print("POSITION ", rb.state[0:3])
                #print("ROTATION ", rb.state[3:12])
                #print("L. MOMENTUM ", rb.state[12:15])
                #print("A. MOMENTUM ", rb.state[15:18])

                

                angle, axis = rb.get_angle_2d()
                if axis[2] < 0:
                    angle *= -1.

                pos = (i.rect.x, i.rect.y)
                
                print("STATE", rb.state[0:3])
                print("POS", pos)
                print("RECT", i.rect.x, i.rect.y)
                print("ANGLE", angle)
                
                #i.update(pos[0] , pos[1])
                #i.update(rb.state[0], rb.state[1])
                if pos[1] >= 550:
                    enemy_objs.remove(i)
                else:
                    i.rotate(angle)
                    i.fall(i.rect.y)
                    i.draw(screen)
                    pygame.display.update()
                    
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
