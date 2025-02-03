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
        self.font = pygame.font.Font(os.path.join('data', 'misc', 'coopbl.ttf'), 28)

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

            elif self.state == STATE_DAMAGE:
                rectlist = self.draw_update_ground()
                if ((time.time() - self.timer) > 4) and (self.check_damage == True):
                    self.check_damage = False
                    self.timer = time.time()
                    defeated_tank = self.show_damage()
                    if defeated_tank != None:
                        self.timer = time.time()
                        exploded = False
                        showing_score = False
                elif ((time.time() - self.timer) > 5) and (self.check_damage == False):
                    self.state = STATE_GAME
                self.eventCheckWaiting()

            elif self.state == STATE_GAME:
                rectlist = self.draw_update_ground()
                if ((time.time() - self.timer) > 5) and (self.shell_fired == False):
                    self.control_panel.update(self)
                    rectlist.append(self.panel_rect)
                self.eventCheckGame()

            elif self.state == STATE_END:
                if showing_score == False:
                    if (time.time() - self.timer) > 8:
                        showing_score = True
                        self.show_score()
                        self.timer = time.time()
                    if (exploded == False):
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
                else:
                    if (time.time() - self.timer) > 7:
                        self.start_new_game()
                rectlist = self.draw_update_ground()
                self.eventCheckWaiting()
                
            else:
                pygame.quit()
                exit(0)
            
            if len(self.fade) != 0:
                rectlist = (draw_fading(self, rectlist))
                
            pygame.display.update(rectlist)
            
            clear_fading(self)
            self.sprites.clear(self.screen, self.background)

    def draw_update_ground(self):
        if (time.time() - self.update_ground_timer) > 0.5:
            self.background = update_screen(self)
        self.sprites.update(self)
        rectlist = self.sprites.draw(self.screen)
        if (time.time() - self.update_ground_timer) > 0.5:
            rectlist.append(self.ground_rect)
            self.update_ground_timer = time.time()
        return rectlist

    def eventCheckMenu(self):
        """ Check input in the menu """
        for event in pygame.event.get():
            if event.type == QUIT:
                self.state = STATE_QUIT
                break
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
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
                        if self.game_started == True:
                            self.state = STATE_GAME
                            self.fade = []
                            self.background = update_screen(self)
                            pygame.display.update()
                            self.menu.new_game_selected = False
                            self.menu.players_selected = False
                            break
                        else:
                            self.state = STATE_QUIT
                            break
                            
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == LEFT_BUTTON:
                    self.menu.check_mouse_event(self, event.pos)

        if self.start_game == True:
            self.score = [0,0]
            self.start_new_game()
            return
            
        if self.menu.update_screen == True:
            self.menu.draw()
            self.menu.update_screen = False
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
                    break

        if ((time.time() - self.timer) > 5) and (self.shell_fired == False):
            self.control_panel.check_mouse_event(self)

    def eventCheckWaiting(self):
        """ Check input while waiting, showing damage, ending, etc. """
        for event in pygame.event.get():
            if event.type == QUIT:
                self.state = STATE_QUIT
                break     

    def start_new_game(self):
        self.sprites.empty()
        self.start_game = False
        self.game_started = True
        self.check_damage = False
        self.update_ground_timer = time.time()
        if random.randint(0,1) == 0:
            self.turn = "left"
        else:
            self.turn = "right"
        if self.number_players == 1:
            if random.randint(0,1) == 0:
                self.player1 = "Player"
                self.player2 = "CPU"
            else:
                self.player1 = "CPU"
                self.player2 = "Player"
        else:
            self.player1 = "Player"
            self.player2 = "Player"
            
        self.ground, self.max_height = new_ground()
        self.ground_rect = pygame.Rect(0, 549-self.max_height, 800, self.max_height+50)
        
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
        self.trees = []
        generate_trees(self)
        self.sprites.add(self.trees)

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

    def change_turn(self):
        for tank in self.tanks:
            tank.time_to_fire = int((float(100-tank.damage)/100)*14)
        self.state = STATE_DAMAGE
        self.check_damage = True
        if self.turn == "left":
            self.turn = "right"
        else:
            self.turn = "left"
        self.shell_fired = False
        self.control_panel.display = True
        self.timer = time.time()
        self.control_panel.update_wind = True
        
    def initialize_game(self):
        self.start_game = False
        self.game_started = False
        self.state = STATE_MENU
        self.menu.draw()
        self.fade = []
        self.fade.append(Fade_in(self.screen.get_rect()))
        pygame.display.update()
        self.background = self.screen.copy()

    def show_damage(self):
        show_damage = False
        for tank in self.tanks:
            if tank.damaged == True:
                if tank.damage >= 100:
                    self.state = STATE_END
                    if tank.position == "left":
                        self.score[1] += 1
                    else:
                        self.score[0] += 1
                    return tank
                show_damage = True
                tank.damaged = False
                damage = self.font.render("DAMAGE REPORT : "+str(tank.damage)+" %", True, (0,0,0))
                if tank.position == "left":
                    self.screen.blit(damage, (15,90))
                    self.background.blit(damage, (15,90))
                elif tank.position == "right":
                    self.screen.blit(damage, (415,90))
                    self.background.blit(damage, (415,90))

        if show_damage == False:
            return None
        pygame.display.update()
        self.sound.play("alarm")
        return None

    def show_score(self):
        self.screen.blit(self.mountains, (0, 0))
        draw_ground(self)
        score1 = self.font.render("SCORE : "+str(self.score[0]), True, (0,0,0))
        score2 = self.font.render("SCORE : "+str(self.score[1]), True, (0,0,0))
        self.screen.blit(score1, (110,90))
        self.screen.blit(score2, (550,90))
        pygame.display.update()
        self.background = self.screen.copy()
            

def play_intro(Game):
#    for tank in Game.tanks:
#        if tank.position == "left":
#            for x in range(0, 100):
#                tank.intro(x, Game.ground)
#                Game.screen.blit(tank.intro_image, tank...
                
        
    #Game.sprites.add(Game.tanks, Game.guns)
    Game.state = STATE_GAME



        
