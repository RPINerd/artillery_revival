#!/usr/bin/env python

import pygame, time, os
from pygame.locals import *
from config import *
from menu import Menu
from fade import *
from background import *
from tank import *
from control_panel import Control_panel
from sound import Sound
from explosion import Smoke

if not pygame.font: print 'Warning, fonts disabled'


class Game(object):
    """ Game """
    def __init__(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.mixer.pre_init(44100,-16, 2, 4096)
        pygame.init()
        if FULL_SCREEN == True:
            if os.name == "nt":
                self.screen = pygame.display.set_mode(SCREEN_SIZE, FULLSCREEN|HWSURFACE|DOUBLEBUF, COLOR_DEPTH)
            else:
                self.screen = pygame.display.set_mode(SCREEN_SIZE, FULLSCREEN, COLOR_DEPTH)
        else:
            self.screen = pygame.display.set_mode(SCREEN_SIZE, 0, COLOR_DEPTH)
            pygame.display.set_caption(GAME_NAME)
            
        self.clock = pygame.time.Clock()
        self.timer = time.time()-5
        self.game_started = False
        self.menu = Menu(self)
        self.sound = Sound()
        self.sprites = pygame.sprite.OrderedUpdates()

        self.initialize_game()

    def main_loop(self):
        """ Main game loop """
        while True:
            self.clock.tick(FRAME_SPEED)
            #self.clock.tick()
            if FULL_SCREEN == False:
                pygame.display.set_caption(GAME_NAME + " FPS: " + str(self.clock.get_fps()))

            rectlist = []
            if self.state == STATE_MENU:
                self.eventCheckMenu()

            elif self.state == STATE_INTRO:
                if len(self.fade) == 0:
                    play_intro(self)
                
            elif self.state == STATE_GAME:
                draw_ground(self)
                self.sprites.update(self)
                rectlist = self.sprites.draw(self.screen)
                rectlist.append(self.ground_rect)
                if ((time.time() - self.timer) > 5) and (self.shell_fired == False):
                    self.control_panel.update(self)
                    rectlist.append(self.panel_rect)
                self.eventCheckGame()

            else:
                pygame.quit()
                exit(0)
                
            if len(self.fade) != 0:
                rectlist = (draw_fading(self, rectlist))
                
            pygame.display.update(rectlist)
            
            clear_fading(self)
            self.sprites.clear(self.screen, self.background)
            

    def eventCheckMenu(self):
        """ Check input in the menu """
        for event in pygame.event.get():
            if event.type == QUIT:
                self.state = STATE_QUIT
                break
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self.game_started == True:
                        self.state = STATE_GAME
                        self.background = update_screen(self)
                        pygame.display.update()
                        return
                    else:
                        if self.menu.new_game_selected == True:
                            if self.menu.players_selected == True:
                                self.menu.players_selected = False
                                self.menu.update_screen = True
                                break
                            else:
                                self.menu.new_game_selected = False
                                self.menu.update_screen = True
                                break
                        else:
                            self.state = STATE_QUIT
                            break
                            
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == LEFT_BUTTON:
                    self.menu.check_mouse_event(self, event.pos)

        if self.start_game == True:
            self.start_new_game()
            return
            
        if self.menu.update_screen == True:
            self.menu.draw()
            self.menu.update_screen = False
            self.fade = []
            self.fade.append(Fade_in(self.menu.update_buttons_rect))
            pygame.display.update()


    def eventCheckGame(self):
        """ Check input in the game """
        for event in pygame.event.get():
            if event.type == QUIT:
                self.state = STATE_QUIT
                break
            elif (event.type == KEYDOWN) and (self.shell_fired == False):
                if (event.key == K_ESCAPE) and (len(self.fade) == 0):
                    self.state = STATE_MENU
                    self.menu.draw()
                    pygame.display.update()
                    self.background = self.screen.copy()
                    return

        if ((time.time() - self.timer) > 5) and (self.shell_fired == False):
            self.control_panel.check_mouse_event(self)

    def start_new_game(self):
        self.sprites.empty()
        self.start_game = False
        self.game_started = True
        if random.randint(0,1) == 0:
            self.turn = "left"
        else:
            self.turn = "right"
        self.ground, self.max_height = new_ground()
        self.ground_rect = pygame.Rect(0, 549-self.max_height, 800, 350)
        
        self.tanks = []
        self.guns = []
        Tank_left = Tank("left", self)
        Gun_left = Gun("left", self)
        Tank_left.gun = Gun_left
        self.tanks.append(Tank_left)
        self.guns.append(Gun_left)
        Tank_right = Tank("right", self)
        Gun_right = Gun("right", self)
        Tank_right.gun = Gun_right
        self.tanks.append(Tank_right)
        self.guns.append(Gun_right)
        self.sprites.add(self.tanks)
        self.sprites.add(self.guns)
        self.shell_fired = False
        Tank_right.ennemy = Tank_left
        Tank_left.ennemy = Tank_right
        
        self.mountains = draw_mountains(pygame.Surface((self.screen.get_size())))
        self.background = update_screen(self)
        
        self.fade = []
        self.fade.append(Fade_in(self.screen.get_rect()))
        pygame.display.update()

        self.control_panel = Control_panel()
        self.panel_rect = pygame.Rect(0, 0, 800, 180)
        self.wind = (10*self.difficulty) + random.randint(-3, 3)
        self.control_panel.update_wind = True

        self.state = STATE_INTRO

    def change_turn(self, tank):
        for tanks in self.tanks:
            tanks.check_damage(self)
        if self.turn == "left":
            self.turn = "right"
        else:
            self.turn = "left"
        tank.time_to_fire = (14 - (14*(tank.damage/100)))
        if tank.time_to_fire > 14:
            tank.time_to_fire = 14
        self.shell_fired = False
        self.control_panel.display = True
        self.timer = time.time()
        self.control_panel.update_wind = True
        
    def initialize_game(self):
        self.start_game = False
        self.game_started = False
        self.sprites.empty()
        self.state = STATE_MENU
        self.menu.draw()
        self.fade = []
        self.fade.append(Fade_in(self.screen.get_rect()))
        pygame.display.update()
        self.background = self.screen.copy()


    def end_game(self, defeated_tank):
        self.timer = time.time()
        explosion_timer = time.time()
        exploded = False
        self.background = update_screen(self)
        pygame.display.update()
        while (time.time() - self.timer) < 10:
            self.clock.tick(FRAME_SPEED)
            if ((time.time() - explosion_timer) > 2) and (exploded == False):
                explosion_timer = time.time()
                exploded = True
                self.sound.play("explosion_tank")
                self.sprites.add(Smoke(defeated_tank.rect.centerx, defeated_tank.rect.centery, self, True, "ground", 90))
                self.sprites.add(Smoke(defeated_tank.rect.centerx, defeated_tank.rect.centery, self, False, "ground", 90))
                self.sprites.add(Smoke(defeated_tank.rect.centerx, defeated_tank.rect.centery-10, self, True, "ground"))
                self.sprites.add(Smoke(defeated_tank.rect.centerx, defeated_tank.rect.centery-10, self, False, "ground"))
                self.sprites.add(Smoke(defeated_tank.rect.centerx, defeated_tank.rect.centery, self, True, "tank", 140))
                self.sprites.add(Smoke(defeated_tank.rect.centerx, defeated_tank.rect.centery, self, False, "tank", 140))
            if ((time.time() - explosion_timer) > 0.5) and (exploded == True):
                explosion_timer = time.time()
                self.sprites.add(Smoke(defeated_tank.rect.centerx, defeated_tank.rect.centery, self, False, "continuous", 150))

            draw_ground(self)
            self.sprites.update(self)
            rectlist = self.sprites.draw(self.screen)
            rectlist.append(self.ground_rect)
            pygame.display.update(rectlist)
            self.sprites.clear(self.screen, self.background)
        self.initialize_game()


def play_intro(Game):
#    for tank in Game.tanks:
#        if tank.position == "left":
#            for x in range(0, 100):
#                tank.intro(x, Game.ground)
#                Game.screen.blit(tank.intro_image, tank...
                
        
    #Game.sprites.add(Game.tanks, Game.guns)
    Game.state = STATE_GAME



        
