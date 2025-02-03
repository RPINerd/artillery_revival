#!/usr/bin/env python

import pygame, math
from load_save import load_image
from explosion import *
#from control_panel import *

class Tank(pygame.sprite.Sprite):
    """ The tank object """
    def __init__(self, position, Game):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image('tank.png', 'sprites', -1)
        self.rect = self.image.get_rect()
        self.ground = Game.ground
        self.position = position
        self.time_to_fire = 14
        self.damage = 0

        #self.intro_image = Tank.image.copy()
        #self.intro_image.blit(load_image('gun.png', 'sprites', -1), (38,4))
        #self.base_intro_image = self.intro_image
        
        if self.position == "left":
            self.rect.bottomleft = (71,600-self.ground[81])
        elif self.position == "right":
            self.rect.bottomleft = (671,600-self.ground[681])
            self.image = pygame.transform.flip(self.image, 1, 0)
            #self.intro_image = pygame.transform.flip(self.intro_image, 1, 0)
        self.base_image = self.image

    def update(self, Game):
        pass

    def check_damage(self, Game):
        if self.damage >= 100:
            #for i in range(0,2):
            #    Game.sprites.add(Smoke(self.rect.centerx, self.rect.centery, Game, True, "ground"))
            #    Game.sprites.add(Smoke(self.rect.centerx, self.rect.centery, Game, False, "ground"))
            Game.end_game(self)

    def stain_black(self, shell_x, shell_y):
        x = int(shell_x) - self.rect.left
        y = int(shell_y) - self.rect.top
        pixel_count = 0
        self.image.lock()
        for i in range(1,20):
            for angles in range(0,360,6):
                pixel_x = int(x + math.sin(math.radians(angles))*i)
                pixel_y = int(y + math.cos(math.radians(angles))*i)
                if pixel_x > (self.rect.width-1): continue
                if pixel_x < 0: continue
                if pixel_y > (self.rect.height-1): continue
                if pixel_y < 0: continue
                color = self.image.get_at((pixel_x, pixel_y))
                if color != (255, 125, 255):
                    self.image.set_at((pixel_x, pixel_y), (int(color[0]*0.6),int(color[1]*0.6),int(color[2]*0.6)))
                    pixel_count += 1
        self.image.unlock()
        return pixel_count

    def intro(self, x, ground):
        pass
        


class Gun(pygame.sprite.Sprite):
    """ The Gun object """
    image = None
    def __init__(self, position, Game):
        pygame.sprite.Sprite.__init__(self)
        if Gun.image is None:
            Gun.image = load_image('gun.png', 'sprites', -1)
        self.image = Gun.image
        self.rect = self.image.get_rect()
        self.position = position
        self.ground = Game.ground
        self.angle = 00
        self.powder = 40
        if self.position == "left":
            self.rect.center = (122,584-self.ground[80])
        elif self.position == "right":
            self.rect.center = (680,584-self.ground[680])
            self.image = pygame.transform.flip(self.image, 1, 0)
        self.base_image = self.image

    def turn(self, ajustment):
        self.angle += ajustment
        if self.angle > 90:
            self.angle = 90
        elif self.angle < 0:
            self.angle = 0
       
        if self.position == "left":
            old_rect = self.rect.bottomleft        
            self.image = pygame.transform.rotate(self.base_image, self.angle)
            self.rect = self.image.get_rect()
            self.rect.bottomleft = old_rect
        elif self.position == "right":
            old_rect = self.rect.bottomright        
            self.image = pygame.transform.rotate(self.base_image, 0 - self.angle)
            self.rect = self.image.get_rect()
            self.rect.bottomright = old_rect

    def update(self, Game):
        pass

class Shell(pygame.sprite.Sprite):
    """ The Shell object """
    image = None
    def __init__(self, tank, ground):
        pygame.sprite.Sprite.__init__(self)
        if Shell.image is None:
            Shell.image = load_image('shell.png', 'sprites', -1)
        self.image = Shell.image
        self.rect = self.image.get_rect()
        self.from_tank = tank
        self.target = tank.ennemy
        if tank.position == "left":
            self.rect.center = tank.gun.rect.topright
            self.speed_x = math.sin(math.radians(90-tank.gun.angle)) * (float(tank.gun.powder+5)/7)
            self.speed_y = (0 - math.cos(math.radians(90-tank.gun.angle))) * (float(tank.gun.powder+5)/7)
        elif tank.position == "right":
            self.rect.center = tank.gun.rect.topleft
            self.speed_x = (0 - math.sin(math.radians(90-tank.gun.angle))) * (float(tank.gun.powder+5)/7)
            self.speed_y = (0 - math.cos(math.radians(90-tank.gun.angle))) * (float(tank.gun.powder+5)/7)
        self.pos_x = self.rect.centerx
        self.pos_y = self.rect.centery
        self.weight = 55

    def update(self, Game):
        self.pos_x += self.speed_x
        if (self.pos_x >= 779) or (self.pos_x <= 21):
            Game.sprites.remove(self)
            Game.change_turn(self.from_tank)
        self.pos_y += self.speed_y
        if (self.pos_y >= 590):
            Game.sprites.remove(self)
            Game.change_turn(self.from_tank)
        self.rect.centerx, self.rect.centery = int(self.pos_x), int(self.pos_y)
        self.speed_y = gravity(self.speed_y, self.weight)
        self.speed_x = apply_wind(self.speed_x, self.weight, Game)
        
        for collide in pygame.sprite.spritecollide(self, Game.sprites, 0):
            if collide in (self.from_tank, self.target):
                if self.confirm_collision(collide) == True:
                    self.explode(Game, collide)
        
        if int(self.pos_y) >= (598-Game.ground[int(self.pos_x)]):
            self.explode(Game)
            #explosion(int(self.pos_x), int(self.pos_y), Game)
            #Game.sprites.remove(self)
            #Game.change_turn(self.from_tank)

    def explode(self, Game, collide=None):
        if collide != None:
            damage = collide.stain_black(self.pos_x, self.pos_y)
            collide.damage += int(damage/10)
            Game.screen.blit(collide.image, collide.rect)
        explosion(int(self.pos_x), int(self.pos_y), Game)
        Game.sprites.remove(self)
        Game.change_turn(self.from_tank)

    def confirm_collision(self, target):
        if target.rect.collidepoint(int(self.pos_x), int(self.pos_y)) == True:
            adjusted_x = int(self.pos_x) - target.rect.left
            adjusted_y = int(self.pos_y) - target.rect.top
            if target.image.get_at((adjusted_x, adjusted_y)) != target.image.get_colorkey():
                return True
            else:
                return False
        else:
            return False








