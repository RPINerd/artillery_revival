""""""

import os
import random
import sys
import time
from pathlib import Path

import pygame
from pygame.locals import DOUBLEBUF, FULLSCREEN, HWSURFACE, K_ESCAPE, KEYDOWN, MOUSEBUTTONDOWN, QUIT

from .background import draw_ground, draw_mountains, generate_trees, new_ground, update_screen
from .config import (
    COLOR_DEPTH,
    FRAME_SPEED,
    FULL_SCREEN,
    GAME_NAME,
    LEFT_BUTTON,
    SCREEN_SIZE,
    STATE_DAMAGE,
    STATE_END,
    STATE_GAME,
    STATE_INTRO,
    STATE_MENU,
    STATE_QUIT,
)
from .control_panel import ControlPanel
from .explosion import Smoke
from .fade import FadeIn, clear_fading, draw_fading
from .menu import Menu
from .sound import Sound
from .tank import TANK_HEALTH, Gun, Tank

if not pygame.font:
    print("Warning, fonts disabled")


class Game:

    """Game"""

    def __init__(self) -> None:
        """"""
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.mixer.pre_init(44100, -16, 2, 4096)
        pygame.init()
        if FULL_SCREEN:
            if os.name == "nt":  # Windows
                self.screen = pygame.display.set_mode(SCREEN_SIZE, FULLSCREEN | HWSURFACE | DOUBLEBUF, COLOR_DEPTH)
            else:
                self.screen = pygame.display.set_mode(SCREEN_SIZE, FULLSCREEN, COLOR_DEPTH)
        else:
            self.screen = pygame.display.set_mode(SCREEN_SIZE, 0, COLOR_DEPTH)
            pygame.display.set_caption(GAME_NAME)

        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.timer: float = time.time() - 5
        self.game_started: bool = False
        self.menu: Menu = Menu(self)
        self.sound: Sound = Sound()
        self.sprites: pygame.sprite.OrderedUpdates = pygame.sprite.OrderedUpdates()
        self.font = pygame.font.Font(Path.joinpath(Path.cwd(), "data", "misc", "COOPBL.ttf"), 28)

        self.initialize_game()

    def main_loop(self) -> None:
        """Main game loop"""
        while True:
            self.clock.tick(FRAME_SPEED)
            if not FULL_SCREEN:
                pygame.display.set_caption(GAME_NAME + " FPS: " + str(self.clock.get_fps()))

            rectlist = []
            if self.state == STATE_MENU:
                self.event_check_menu()

            elif self.state == STATE_INTRO:
                if len(self.fade) == 0:
                    play_intro(self)

            elif self.state == STATE_DAMAGE:
                rectlist = self.draw_update_ground()
                if ((time.time() - self.timer) > 4) and self.check_damage:
                    self.check_damage = False
                    self.timer = time.time()
                    defeated_tank = self.show_damage()
                    if defeated_tank is not None:
                        self.timer = time.time()
                        exploded = False
                        showing_score = False
                elif ((time.time() - self.timer) > 5) and not self.check_damage:
                    self.state = STATE_GAME
                self.event_check_waiting()

            elif self.state == STATE_GAME:
                rectlist = self.draw_update_ground()
                if ((time.time() - self.timer) > 5) and not self.shell_fired:
                    self.control_panel.update(self)
                    rectlist.append(self.panel_rect)
                self.event_check_game()

            elif self.state == STATE_END:
                if not showing_score:
                    if (time.time() - self.timer) > 8:
                        showing_score = True
                        self.show_score()
                        self.timer = time.time()
                    if not exploded:
                        explosion_timer = time.time()
                        exploded = True
                        self.sound.play("explosion_tank")
                        self.sprites.add(Smoke(defeated_tank.rect.centerx, defeated_tank.rect.centery, True, "ground", 90))
                        self.sprites.add(Smoke(defeated_tank.rect.centerx, defeated_tank.rect.centery, False, "ground", 90))
                        self.sprites.add(Smoke(defeated_tank.rect.centerx, defeated_tank.rect.centery - 10, True, "ground"))
                        self.sprites.add(Smoke(defeated_tank.rect.centerx, defeated_tank.rect.centery - 10, False, "ground"))
                        self.sprites.add(Smoke(defeated_tank.rect.centerx, defeated_tank.rect.centery, True, "tank", 140))
                        self.sprites.add(Smoke(defeated_tank.rect.centerx, defeated_tank.rect.centery, False, "tank", 140))
                    if ((time.time() - explosion_timer) > 0.5) and exploded:
                        explosion_timer = time.time()
                        self.sprites.add(Smoke(defeated_tank.rect.centerx, defeated_tank.rect.centery, False, "continuous", 150))
                elif (time.time() - self.timer) > 7:
                    self.start_new_game()
                rectlist = self.draw_update_ground()
                self.event_check_waiting()

            else:
                pygame.quit()
                sys.exit(0)

            if len(self.fade) != 0:
                rectlist = (draw_fading(self, rectlist))

            pygame.display.update(rectlist)

            clear_fading(self)
            self.sprites.clear(self.screen, self.background)

    def draw_update_ground(self) -> list:
        """"""
        if (time.time() - self.update_ground_timer) > 0.5:
            self.background = update_screen(self)
        self.sprites.update(self)
        rectlist = self.sprites.draw(self.screen)
        if (time.time() - self.update_ground_timer) > 0.5:
            rectlist.append(self.ground_rect)
            self.update_ground_timer = time.time()
        return rectlist

    def event_check_menu(self) -> None:
        """Check input in the menu"""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.state = STATE_QUIT
                break
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self.menu.new_game_selected:
                        if self.menu.players_selected:
                            self.menu.players_selected = False
                            self.menu.update_screen = True
                            break
                        self.menu.new_game_selected = False
                        self.menu.update_screen = True
                        break
                    if self.game_started:
                        self.state = STATE_GAME
                        self.fade = []
                        self.background = update_screen(self)
                        pygame.display.update()
                        self.menu.new_game_selected = False
                        self.menu.players_selected = False
                        break
                    self.state = STATE_QUIT
                    break

            elif event.type == MOUSEBUTTONDOWN and event.button == LEFT_BUTTON:
                self.menu.check_mouse_event(self, event.pos)

        if self.start_game:
            self.score = [0, 0]
            self.start_new_game()
            return

        if self.menu.update_screen:
            self.menu.draw()
            self.menu.update_screen = False
            pygame.display.update()

    def event_check_game(self) -> None:
        """Check input in the game"""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.state = STATE_QUIT
                break
            if (event.type == KEYDOWN) and not self.shell_fired:
                if (event.key == K_ESCAPE) and (len(self.fade) == 0):
                    self.state = STATE_MENU
                    self.menu.draw()
                    pygame.display.update()
                    self.background = self.screen.copy()
                    break

        if ((time.time() - self.timer) > 5) and not self.shell_fired:
            self.control_panel.check_mouse_event(self)

    def event_check_waiting(self) -> None:
        """Check input while waiting, showing damage, ending, etc."""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.state = STATE_QUIT
                break

    def start_new_game(self) -> None:
        """"""
        self.sprites.empty()
        self.start_game = False
        self.game_started = True
        self.check_damage = False
        self.update_ground_timer = time.time()
        if random.randint(0, 1) == 0:
            self.turn = "left"
        else:
            self.turn = "right"
        if self.number_players == 1:
            if random.randint(0, 1) == 0:
                self.player1 = "Player"
                self.player2 = "CPU"
            else:
                self.player1 = "CPU"
                self.player2 = "Player"
        else:
            self.player1 = "Player"
            self.player2 = "Player"

        self.ground, self.max_height = new_ground()
        self.ground_rect = pygame.Rect(0, 549 - self.max_height, 800, self.max_height + 50)

        self.tanks: list[Tank] = []
        self.guns: list[Gun] = []

        left_gun: Gun = Gun("left", self)
        right_gun = Gun("right", self)
        self.guns = [left_gun, right_gun]

        left_tank: Tank = Tank("left", left_gun, self)
        right_tank = Tank("right", right_gun, self)
        self.tanks = [left_tank, right_tank]

        self.sprites.add(self.tanks)
        self.sprites.add(self.guns)

        self.shell_fired = False

        right_tank.ennemy = left_tank
        left_tank.ennemy = right_tank

        self.trees = []
        generate_trees(self)
        self.sprites.add(self.trees)

        self.mountains = draw_mountains(pygame.Surface(self.screen.get_size()))
        self.background = update_screen(self)

        self.fade = []
        self.fade.append(FadeIn(self.screen.get_rect()))
        pygame.display.update()

        self.control_panel = ControlPanel()
        self.panel_rect = pygame.Rect(0, 0, 800, 180)
        self.wind = (10 * self.difficulty) + random.randint(-3, 3)
        self.control_panel.update_wind = True

        self.state = STATE_INTRO

    def change_turn(self) -> None:
        """"""
        for tank in self.tanks:
            tank.time_to_fire = int((float(100 - tank.damage) / 100) * 14)
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

    def initialize_game(self) -> None:
        """"""
        self.start_game = False
        self.game_started = False
        self.state = STATE_MENU
        self.menu.draw()
        self.fade = []
        self.fade.append(FadeIn(self.screen.get_rect()))
        pygame.display.update()
        self.background = self.screen.copy()

    def show_damage(self) -> Tank:
        """"""
        show_damage = False
        for tank in self.tanks:
            if tank.damaged:
                if tank.damage >= TANK_HEALTH:
                    self.state = STATE_END
                    if tank.position == "left":
                        self.score[1] += 1
                    else:
                        self.score[0] += 1
                    return tank
                show_damage = True
                tank.damaged = False
                damage = self.font.render("DAMAGE REPORT : " + str(tank.damage) + " %", True, (0, 0, 0))
                if tank.position == "left":
                    self.screen.blit(damage, (15, 90))
                    self.background.blit(damage, (15, 90))
                elif tank.position == "right":
                    self.screen.blit(damage, (415, 90))
                    self.background.blit(damage, (415, 90))

        if not show_damage:
            return None
        pygame.display.update()
        self.sound.play("alarm")
        return None

    def show_score(self) -> None:
        """"""
        self.screen.blit(self.mountains, (0, 0))
        draw_ground(self)
        score1 = self.font.render("SCORE : " + str(self.score[0]), True, (0, 0, 0))
        score2 = self.font.render("SCORE : " + str(self.score[1]), True, (0, 0, 0))
        self.screen.blit(score1, (110, 90))
        self.screen.blit(score2, (550, 90))
        pygame.display.update()
        self.background = self.screen.copy()


def play_intro(game: Game) -> None:
    """"""
    # for tank in game.tanks:
    #     if tank.position == "left":
    #         for x in range(0, 100):
    #             tank.intro(x, game.ground)
    #             game.screen.blit(tank.intro_image, tank...

    # game.sprites.add(game.tanks, game.guns)
    game.state = STATE_GAME
