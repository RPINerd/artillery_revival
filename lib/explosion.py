#!/usr/bin/env python

import pygame, random, math, time
from pygame.locals import *
from background import update_screen
from load_save import *
from config import *


def explosion(exp_x, exp_y, Game):
    particles = []
    Game.sound.play("explosion_ground")

    Game.screen.lock()
    for i in range(1,17):
        for angles in range(0,360,3):
            x = int(exp_x + math.sin(math.radians(angles))*i)
            y = int(exp_y + math.cos(math.radians(angles))*i)
            if y > 590: y = 590
            if x <= 1: x = 0
            elif x >= 798: x = 799
            color = Game.screen.get_at((x, y))
            if color != (120, 80, 50, 255):
                Game.screen.set_at((x, y), (120, 80, 50))
                if (exp_x - x) == 0:
                    speed_x = (random.random()*4)-2
                else:
                    speed_x = (3/(exp_x - x)*random.random())
                if (exp_y - y) == 0:
                    speed_y = (random.random()*2)-1.2
                else:
                    speed_y = (3/(exp_y - y)*random.random()*2)-1
                if random.randint(0,3) != 0:
                    particle = Particle(color, x, y, speed_x, speed_y)
                    particles.append(particle)
                if y >= (600-Game.ground[x]):
                    Game.ground[x] = 599 - y
                while color != (120, 80, 50, 255):
                    y -= 1
                    color = Game.screen.get_at((x, y))
                    if random.randint(0,40) == 0:
                        speed_x = 0.0
                        speed_y = 1.5
                        particle = Particle(color, x, y, speed_x, speed_y)
                        particles.append(particle)
    Game.screen.unlock()

    for i in range(-12,-23,-1):
        Game.ground[exp_x+i-1] = Game.ground[exp_x+i] + int((Game.ground[exp_x+i-1] - Game.ground[exp_x+i])*0.35)
    for i in range(12,23):
        Game.ground[exp_x+i+1] = Game.ground[exp_x+i] + int((Game.ground[exp_x+i+1] - Game.ground[exp_x+i])*0.35)

    Game.sprites.add(particles)
    Game.sprites.add(Smoke(exp_x, exp_y, Game, True, "ground"))
    Game.sprites.add(Smoke(exp_x, exp_y, Game, False, "ground"))
    #flare(exp_x, exp_y, Game) 
    Game.background = update_screen(Game)


class Particle(pygame.sprite.Sprite):
    """ The particle object """
    def __init__(self, color, x, y, speed_x, speed_y):
        pygame.sprite.Sprite.__init__(self)
        self.width = random.randint(1,3)
        self.height = random.randint(1,3)
        image = pygame.Surface((self.width,self.height))
        image.fill(color)
        self.image = image
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.weight = (self.width*self.height*20)+20
        
    def update(self, Game):
        self.x += self.speed_x
        if (int(self.x > 795)) or (int(self.x < 5)):
            Game.sprites.remove(self)
        self.y += self.speed_y
        
        if self.speed_x > 0:
            if (599-Game.ground[int(self.x)+1]) < (int(self.y)):
                self.speed_x = (0-self.speed_x)*0.15
        elif self.speed_x < 0:
            if (599-Game.ground[int(self.x)-1]) < (int(self.y)):
                self.speed_x = (0-self.speed_x)*0.15
                    
        if int(self.y) >= (599-Game.ground[int(self.x)]):
            self.speed_y = (0-self.speed_y)*0.1
            self.speed_x *= 0.7
            self.y = 599-Game.ground[int(self.x)]
            
        self.rect.centerx, self.rect.centery = int(self.x), int(self.y)
        self.speed_y = gravity(self.speed_y, self.weight)
        self.speed = math.hypot(self.speed_x, self.speed_y)
        
        if (self.speed < 0.4) and ((599-int(self.y)) == Game.ground[int(self.x)]):
            Game.sprites.remove(self)
            if random.randint(0,1) == 0:
                if (Game.ground[int(self.x)-1] - Game.ground[int(self.x)]) > 1:
                    Game.ground[int(self.x)] += 1
                elif (Game.ground[int(self.x)+1] - Game.ground[int(self.x)]) > 1:
                    Game.ground[int(self.x)] += 1
                elif (Game.ground[int(self.x)-1] - Game.ground[int(self.x)]) < -1:
                    Game.ground[int(self.x)-1] += 1
                elif (Game.ground[int(self.x)+1] - Game.ground[int(self.x)]) < -1:
                    Game.ground[int(self.x)+1] += 1
                else:
                    Game.ground[int(self.x)] += 1
        self.speed_x = apply_wind(self.speed_x, self.weight, Game)


class Smoke(pygame.sprite.Sprite):
    """ The smoke object """
    images = {}
    images[1] = load_image_alpha('smoke1.png', 'sprites/smoke')
    images[2] = load_image_alpha('smoke2.png', 'sprites/smoke')
    images[3] = load_image_alpha('smoke3.png', 'sprites/smoke')
    images[4] = load_image_alpha('smoke4.png', 'sprites/smoke')
    images[5] = load_image_alpha('smoke5.png', 'sprites/smoke')
    images[6] = load_image_alpha('smoke6.png', 'sprites/smoke')
    def __init__(self, x, y, Game, rotate_clockwise=True, smoke_type=None, max_size=130):
        pygame.sprite.Sprite.__init__(self)
        self.image = Smoke.images[random.randint(1,6)].convert_alpha()
        self.rect = self.image.get_rect(center = (x, y))
        self.blending_color = pygame.Surface((self.image.get_size()), SRCALPHA)
        self.blending_color.fill((1,1,1,0))
        self.blending_alpha = pygame.Surface((self.image.get_size()), SRCALPHA)
        self.blending_alpha.fill((0,0,0,1))
        self.angle = random.randint(0,359)
        self.speed_y = (random.random()/15)-0.1
        self.max_size = max_size
        
        if smoke_type == "ground":
            self.y = y - 5
            if rotate_clockwise == False:
                self.angle_adjust = random.random()+0.4
                self.x = x + random.randint(7,14)
                self.speed_x = (random.random()/8)+0.06
            else:
                self.angle_adjust = random.random()-1.4
                self.x = x - random.randint(7,14)
                self.speed_x = (random.random()/8)-0.19

        elif smoke_type == "gun":
            self.x = x
            self.y = y
            self.speed_x = 0
            if rotate_clockwise == False:
                self.angle_adjust = random.random()+0.2
            else:
                self.angle_adjust = random.random()-1.2

        elif smoke_type == "tank":
            self.y = y - 3
            self.speed_y = -1.2
            if rotate_clockwise == False:
                self.angle_adjust = random.random()+1
                self.x = x + random.randint(12,16)
                self.speed_x = (random.random()/8)+0.055
            else:
                self.angle_adjust = random.random()-2
                self.x = x - random.randint(12,16)
                self.speed_x = (random.random()/8)-0.18

        elif smoke_type == "continuous":
            self.x = x
            self.y = y
            self.speed_x = 0
            self.angle_adjust = 0
            self.speed_y = -0.7

            
        self.lifespan = 1.0
        scale = self.lifespan/self.max_size
        self.base_image = self.image
        self.base_image_rect = self.base_image.get_rect()
        self.image = pygame.transform.scale(self.base_image, (int(self.base_image_rect.width*scale), int(self.base_image_rect.height*scale)))
        self.weight = 30
        
    def update(self, Game):
        scale = self.lifespan/self.max_size
        self.image = pygame.transform.scale(self.base_image, (int(self.base_image_rect.width*scale), int(self.base_image_rect.height*scale)))
        if self.angle_adjust != 0:
            self.angle += self.angle_adjust
            if self.angle > 360:
                self.angle -= 360
            elif self.angle < 0:
                self.angle += 360
            self.angle_adjust *= 0.995
        self.speed_x *= 0.995
        self.speed_y -= 0.0005
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_x = apply_wind(self.speed_x, self.weight, Game)
        self.image = pygame.transform.rotate(self.image, int(self.angle))
        self.rect = self.image.get_rect(center = (int(self.x), int(self.y)))
    
        if random.randint(0,4) == 0:
            self.base_image.blit(self.blending_color, (0,0), None, BLEND_RGBA_ADD)
        self.base_image.blit(self.blending_alpha, (0,0), None, BLEND_RGBA_SUB)

        self.lifespan += ((100-self.lifespan)/40)
        if self.lifespan >= 99.98:
            Game.sprites.remove(self)


def flare(x, y, Game):
    ## Currently disabled
    image = load_image('flare.png', 'sprites/effects', (0,0,0))
    rect = image.get_rect(center = (x, y))
    for tank in Game.tanks:
        Game.screen.blit(tank.image, tank.rect)
    Game.screen.blit(image, rect, None, BLEND_RGB_ADD)
    pygame.display.update(rect)



def gravity(speed_y, weight):
    ajustment = weight / GRAVITY
    speed_y = speed_y + ajustment
    if speed_y > 8.0:
        speed_y = 8.0
    return speed_y

def apply_wind(speed_x, weight, Game):
    wind_difference = Game.wind - (speed_x*5)
    air_resistance = 1 - (abs(wind_difference) / weight / 250)
    wind_ajustment = (wind_difference / weight / 60)
    speed_x = (speed_x * air_resistance) + wind_ajustment
    return speed_x





