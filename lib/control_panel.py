""""""

import random
import time
from pathlib import Path
from typing import TYPE_CHECKING

import pygame
from pygame.locals import BLEND_RGB_ADD, BLEND_RGB_MULT, BLEND_RGB_SUB

from .background import update_screen
from .config import FRAME_SPEED
from .explosion import Smoke
from .load_save import load_image, load_music
from .tank import Shell

if TYPE_CHECKING:
    from .game import Game
    from .tank import Tank


class ControlPanel:

    """Object containing all the control panel elements that are across the top of the screen"""

    def __init__(self) -> None:
        """"""
        self.screen: pygame.Surface = pygame.display.get_surface()
        self.image: pygame.Surface = load_image("panel.png", "sprites", -1)
        self.timer_image: pygame.Surface = load_image("timer.png", "sprites/effects", (255, 255, 255, 255))
        self.wind_image: pygame.Surface = load_image("wind.png", "sprites/effects", (255, 255, 255, 255))
        self.barrel_powder_image: pygame.Surface = load_image("barrel_powder.png", "sprites/effects", (255, 255, 255, 255))
        self.rect: pygame.Rect = self.image.get_rect(topleft=(0, 0))
        self.display: bool = True
        self.font: pygame.font.Font = pygame.font.Font(Path.joinpath(Path.cwd(), "data", "misc", "COOPBL.ttf"), 36)
        self.font_timer: pygame.font.Font = pygame.font.Font(Path.joinpath(Path.cwd(), "data", "misc", "COOPBL.ttf"), 30)
        self.player_timer: float = time.time()
        self.highlight_button: bool = False
        self.button_shadowed: pygame.Surface = pygame.Surface((34, 34))
        self.button_shadowed.fill((60, 60, 60))
        self.button_timer: float = time.time()
        self.timer_digit1: float = time.time()
        self.timer_digit2: float = time.time()
        self.spy_cam: pygame.Surface = pygame.Surface((194, 94))
        self.spy_cam_static: pygame.Surface = load_image("static.png", "sprites/effects", 0)
        self.spy_cam_good_signal: bool = True
        self.glare: pygame.Surface = load_image("glare.png", "sprites/effects", (255, 255, 255, 255))

        self.player_rect: dict[str, pygame.Rect] = {}
        self.player_rect["left"] = pygame.Rect(33, 62, 34, 34)
        self.player_rect["right"] = pygame.Rect(243, 62, 34, 34)
        self.button_up_barrel_rect: pygame.Rect = pygame.Rect(193, 84, 34, 34)
        self.button_down_barrel_rect: pygame.Rect = pygame.Rect(83, 84, 34, 34)
        self.barrel_rect: pygame.Rect = pygame.Rect(122, 84, 66, 34)
        self.button_up_powder_rect: pygame.Rect = pygame.Rect(682, 84, 34, 34)
        self.button_down_powder_rect: pygame.Rect = pygame.Rect(572, 84, 34, 34)
        self.powder_rect: pygame.Rect = pygame.Rect(611, 84, 66, 34)
        self.button_fire_rect: pygame.Rect = pygame.Rect(732, 23, 34, 73)
        self.wind_rect: pygame.Rect = pygame.Rect(650, 23, 66, 34)

    def update(self, game: "Game") -> None:
        """"""
        self.screen.blit(self.image, self.rect)
        tanks = {}
        for tank in game.tanks:
            tanks[tank.position] = tank
        tank = tanks[game.turn]

        text = self.font.render(str(tank.gun.angle), True, (138, 11, 17))
        self.screen.blit(text, (self.barrel_rect.centerx - (text.get_width() / 2), self.barrel_rect.centery - (text.get_height() / 2) - 3))
        text = self.font.render(str(tank.gun.powder), True, (138, 11, 17))
        self.screen.blit(text, (self.powder_rect.centerx - (text.get_width() / 2), self.powder_rect.centery - (text.get_height() / 2) - 3))
        self.screen.blit(self.barrel_powder_image, (122, 84), None, BLEND_RGB_MULT)
        self.screen.blit(self.barrel_powder_image, (611, 84), None, BLEND_RGB_MULT)

        if (time.time() - self.player_timer) > 0.4:
            self.player_timer = time.time()
            if not self.highlight_button:
                self.highlight_button = True
            else:
                self.highlight_button = False
            if random.randint(0, 1) == 0:
                if (self.spy_cam_good_signal) and (random.randint(0, 1) == 0):
                    self.spy_cam_good_signal = False
                else:
                    self.spy_cam_good_signal = True

        if self.highlight_button:
            rect = self.player_rect[tank.position]
            self.screen.fill((0, 0, 0), rect)
            if tank.position == "left":
                text = self.font.render("1", True, (205, 205, 205))
            else:
                text = self.font.render("2", True, (205, 205, 205))
            self.screen.blit(text, (rect.centerx - (text.get_width() / 2), rect.centery - (text.get_height() / 2) - 2))

        # Wind
        if self.update_wind:
            self.updating_wind(game)
            self.update_wind = False

        wind1 = int(game.wind / 10)
        wind2 = game.wind - (wind1 * 10)
        text = self.font.render(str(wind1), True, (30, 30, 30))
        x_pos_adjust = self.wind_rect.centerx - ((text.get_width() / 2) + 16)
        x_neg_adjust = self.wind_rect.centerx - ((text.get_width() / 2) - 16)
        y_adjust = self.wind_rect.centery - (text.get_height() / 2) - 3
        self.screen.blit(text, (x_pos_adjust, y_adjust))
        text = self.font.render(str(wind2), True, (30, 30, 30))
        self.screen.blit(text, (x_neg_adjust, y_adjust))
        self.screen.blit(self.wind_image, (650, 23), None, BLEND_RGB_MULT)

        # Center timer
        tank_time1 = int(tank.time_to_fire / 10)
        tank_time2 = tank.time_to_fire - (tank_time1 * 10)
        digit1_top = tank_time1 + 1
        if digit1_top == 10:
            digit1_top = 0
        digit2_top = tank_time2 + 1
        if digit2_top == 10:
            digit2_top = 0

        digit1 = pygame.Surface((27, 48))
        digit2 = pygame.Surface((27, 48))
        color = (255, 255, 255)
        if (tank_time1 == 0) and (tank_time2 <= 4) and self.highlight_button:
            color = (255, 0, 0)
        digit1.fill(color)
        digit2.fill(color)

        text_digit1_top = self.font_timer.render(str(digit1_top), True, (30, 30, 30))
        text_digit1_bottom = self.font_timer.render(str(tank_time1), True, (30, 30, 30))
        text_digit2_top = self.font_timer.render(str(digit2_top), True, (30, 30, 30))
        text_digit2_bottom = self.font_timer.render(str(tank_time2), True, (30, 30, 30))
        digit1.blit(text_digit1_top, (5, -8))
        digit1.blit(text_digit1_bottom, (5, 16))
        digit2.blit(text_digit2_top, (4, -8))
        digit2.blit(text_digit2_bottom, (4, 16))

        digit2_rect_adjust = int((time.time() - self.timer_digit2) * 24)
        if (time.time() - self.timer_digit2) > 1:
            self.timer_digit2 = time.time()
            tank_time2 -= 1
            if tank_time2 == -1:
                if tank_time1 == 0:
                    fire_shell(self, game, tank)
                    return
                tank_time2 = 9
        digit2_rect = pygame.Rect(0, digit2_rect_adjust, 27, 24)

        if tank_time2 == 9:
            digit1_rect_adjust = int((time.time() - self.timer_digit1) * 24)
            if (time.time() - self.timer_digit1) > 1:
                self.timer_digit1 = time.time()
                tank_time1 -= 1
                if tank_time1 == -1:
                    tank_time1 = 9
            digit1_rect = pygame.Rect(0, digit1_rect_adjust, 27, 24)
        else:
            digit1_rect = pygame.Rect(0, 24, 27, 24)
        self.screen.blit(digit1, (373, 133), digit1_rect)
        self.screen.blit(digit2, (400, 133), digit2_rect)
        self.screen.blit(self.timer_image, (373, 133), None, BLEND_RGB_MULT)
        self.screen.blit(self.glare, (375, 141), None, BLEND_RGB_ADD)

        # Spy cam
        if game.turn == "left":
            ennemy = tanks["right"]
        else:
            ennemy = tanks["left"]
        cam_rect = ennemy.rect.copy()
        cam_rect = cam_rect.inflate(134, 72)
        cam_rect.move_ip(0, -10)
        self.spy_cam.blit(game.screen, (0, 0), cam_rect)
        if not self.spy_cam_good_signal:
            static_rect = self.spy_cam.get_rect(topleft=(random.randint(0, 150), random.randint(0, 100)))
            static_rect = static_rect.clamp(self.spy_cam_static.get_rect())
            static = self.spy_cam_static.copy()
            if random.randint(0, 1) == 0:
                static.blit(self.spy_cam, (20, 20), None, BLEND_RGB_SUB)
            else:
                static.blit(self.spy_cam, (20, 20), None, BLEND_RGB_MULT)
            self.screen.blit(static, (303, 23), static_rect)
        else:
            self.screen.blit(self.spy_cam, (303, 23))

        glare = pygame.transform.scale(self.glare, (62, 11))
        self.screen.blit(glare, (124, 97), None, BLEND_RGB_ADD)
        self.screen.blit(glare, (613, 97), None, BLEND_RGB_ADD)
        self.screen.blit(glare, (652, 36), None, BLEND_RGB_ADD)
        glare = pygame.transform.scale(self.glare, (120, 13))
        self.screen.blit(glare, (522, 29), None, BLEND_RGB_ADD)
        glare = pygame.transform.scale(self.glare, (239, 13))
        self.screen.blit(glare, (35, 29), None, BLEND_RGB_ADD)
        self.screen.blit(glare, (35, 129), None, BLEND_RGB_ADD)
        self.screen.blit(glare, (524, 129), None, BLEND_RGB_ADD)
        tank.time_to_fire = (tank_time1 * 10) + tank_time2

    def check_mouse_event(self, game: "Game") -> None:
        """"""
        button1, button2, button3 = pygame.mouse.get_pressed()
        if (button1, button2, button3) == (0, 0, 0):
            pygame.mixer.music.stop()
        pos = pygame.mouse.get_pos()
        for tank in game.tanks:
            if (tank.position == game.turn) and button1:
                if (time.time() - self.button_timer) > 0.07:
                    self.button_timer = time.time()
                    if self.button_up_barrel_rect.collidepoint(pos):
                        check_sound()
                        self.screen.blit(self.button_shadowed, self.button_up_barrel_rect.topleft, None, BLEND_RGB_MULT)
                        tank.gun.turn(1)
                        return
                    if self.button_down_barrel_rect.collidepoint(pos):
                        check_sound()
                        self.screen.blit(self.button_shadowed, self.button_down_barrel_rect.topleft, None, BLEND_RGB_MULT)
                        tank.gun.turn(-1)
                        return

                    if self.button_up_powder_rect.collidepoint(pos):
                        game.sound.play("powder")
                        self.screen.blit(self.button_shadowed, self.button_up_powder_rect.topleft, None, BLEND_RGB_MULT)
                        tank.gun.powder += 1
                        tank.gun.powder = min(tank.gun.powder, 99)
                        return
                    if self.button_down_powder_rect.collidepoint(pos):
                        game.sound.play("powder")
                        self.screen.blit(self.button_shadowed, self.button_down_powder_rect.topleft, None, BLEND_RGB_MULT)
                        tank.gun.powder -= 1
                        tank.gun.powder = max(tank.gun.powder, 10)
                        return
                    pygame.mixer.music.stop()

                if self.button_fire_rect.collidepoint(pos):
                    fire_shell(self, game, tank)

                break
            continue

    def updating_wind(self, game: "Game") -> None:
        """"""
        self.timer_digit1 = time.time()
        self.timer_digit2 = time.time()
        wind_adjusted = game.wind + (random.randint(-3, 3) * game.difficulty)
        if wind_adjusted == game.wind:
            return
        if wind_adjusted < game.wind:
            adjustment = -1
        else:
            adjustment = 1
        wind_adjusted = max(wind_adjusted, 0)

        game.background = update_screen(game)
        game.screen.blit(self.image, self.rect)
        pygame.display.update()

        while True:
            game.clock.tick(FRAME_SPEED)
            game.screen.blit(self.image, self.rect)
            wind1 = int(game.wind / 10)
            wind2 = game.wind - (wind1 * 10)

            digit1_top = wind1 + 1
            if digit1_top == 10:
                digit1_top = 0
            digit1_middle = wind1
            digit1_bottom = wind1 - 1
            if digit1_bottom == -1:
                digit1_bottom = 9

            digit2_top = wind2 + 1
            if digit2_top == 10:
                digit2_top = 0
            digit2_middle = wind2
            digit2_bottom = wind2 - 1
            if digit2_bottom == -1:
                digit2_bottom = 9

            digit1 = pygame.Surface((33, 102))
            digit2 = pygame.Surface((33, 102))
            digit1.fill((255, 255, 255))
            digit2.fill((255, 255, 255))

            text_digit1_top = self.font.render(str(digit1_top), True, (30, 30, 30))
            text_digit1_middle = self.font.render(str(digit1_middle), True, (30, 30, 30))
            text_digit1_bottom = self.font.render(str(digit1_bottom), True, (30, 30, 30))
            text_digit2_top = self.font.render(str(digit2_top), True, (30, 30, 30))
            text_digit2_middle = self.font.render(str(digit2_middle), True, (30, 30, 30))
            text_digit2_bottom = self.font.render(str(digit2_bottom), True, (30, 30, 30))
            digit1.blit(text_digit1_top, (6, -7))
            digit1.blit(text_digit1_middle, (6, 27))
            digit1.blit(text_digit1_bottom, (6, 61))
            digit2.blit(text_digit2_top, (5, -7))
            digit2.blit(text_digit2_middle, (5, 27))
            digit2.blit(text_digit2_bottom, (5, 61))

            if ((wind2 == 0) and (adjustment == -1)) or ((wind2 == 9) and (adjustment == 1)):
                digit1_rect_adjust = int(((time.time() - self.timer_digit1) * 34 * (0 - adjustment)) + 34)
                if (time.time() - self.timer_digit1) > 1:
                    self.timer_digit1 = time.time()
                    wind1 += adjustment
                    if wind1 == -1:
                        wind1 = 9
                    elif wind1 == 10:
                        wind1 = 0
                digit1_rect = pygame.Rect(0, digit1_rect_adjust, 33, 34)
            else:
                digit1_rect = pygame.Rect(0, 34, 33, 34)

            digit2_rect_adjust = int(((time.time() - self.timer_digit2) * 34 * (0 - adjustment)) + 34)
            if (time.time() - self.timer_digit2) > 1:
                self.timer_digit2 = time.time()
                wind2 += adjustment
                game.wind += adjustment
                if wind2 == -1:
                    wind2 = 9
                elif wind2 == 10:
                    wind2 = 0
            digit2_rect = pygame.Rect(0, digit2_rect_adjust, 33, 34)

            self.screen.blit(digit1, (650, 23), digit1_rect)
            self.screen.blit(digit2, (683, 23), digit2_rect)
            self.screen.blit(self.wind_image, (650, 23), None, BLEND_RGB_MULT)
            glare = pygame.transform.scale(self.glare, (62, 11))
            self.screen.blit(glare, (652, 36), None, BLEND_RGB_ADD)

            game.sprites.update(game)
            rectlist = game.sprites.draw(game.screen)
            rectlist.append(self.rect)
            pygame.display.update(rectlist)
            game.sprites.clear(game.screen, game.background)
            pygame.event.pump()

            if game.wind in {wind_adjusted, 0}:
                return


def fire_shell(panel: ControlPanel, game: "Game", tank: "Tank") -> None:
    """"""
    pygame.mixer.music.stop()
    if tank.position == "left":
        game.sprites.add(Smoke(tank.gun.rect.right, tank.gun.rect.top, False, "gun"))
        game.sprites.add(Smoke(tank.gun.rect.left, tank.gun.rect.bottom + 10, True, "gun"))
    else:
        game.sprites.add(Smoke(tank.gun.rect.left, tank.gun.rect.top, True, "gun"))
        game.sprites.add(Smoke(tank.gun.rect.right, tank.gun.rect.bottom + 10, False, "gun"))
    game.sound.play("gun")
    game.shell_fired = True
    panel.display = False
    game.sprites.add(Shell(tank))
    game.background = update_screen(game)
    pygame.display.update()


def check_sound() -> None:
    """"""
    if pygame.mixer.music.get_busy():
        return
    music = load_music("elevation.ogg")
    pygame.mixer.music.play(-1)
