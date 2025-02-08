"""This module contains the FadeIn and FadeOut classes, which are used to create a fade in/out effect for the screen."""

from typing import TYPE_CHECKING

import pygame
from pygame.locals import BLEND_RGB_MULT

if TYPE_CHECKING:
    from .game import Game


class FadeIn:
    """"""
    def __init__(self, rect: pygame.Rect) -> None:
        """"""
        self.rect: pygame.Rect = rect
        self.screen: pygame.Surface = pygame.display.get_surface()
        self.image: pygame.Surface = pygame.Surface(rect.size)
        self.color: int = 0
        self.image.fill((self.color, self.color, self.color))
        self.finished: bool = False
        self.background: pygame.Surface = self.image.copy()
        self.background.blit(self.screen, (0, 0), rect)
        self.screen.fill((0, 0, 0), rect)

    def update(self) -> pygame.Rect:
        """"""
        self.color += 5
        self.image.fill((self.color, self.color, self.color))
        self.screen.blit(self.image, self.rect, None, BLEND_RGB_MULT)
        if self.color == 255:
            self.finished = True
        return self.rect

    def clear(self) -> None:
        """"""
        self.screen.blit(self.background, self.rect)


class FadeOut:
    """"""
    def __init__(self, rect: pygame.Rect) -> None:
        """"""
        self.rect: pygame.Rect = rect
        self.screen: pygame.Surface = pygame.display.get_surface()
        self.image: pygame.Surface = pygame.Surface(rect.size)
        self.color: int = 255
        self.image.fill((self.color, self.color, self.color))
        self.finished: bool = False
        self.background: pygame.Surface = self.image.copy()
        self.background.blit(self.screen, (0, 0), rect)

    def update(self) -> pygame.Rect:
        """"""
        self.color -= 5
        self.image.fill((self.color, self.color, self.color))
        self.screen.blit(self.image, self.rect, None, BLEND_RGB_MULT)
        if self.color == 0:
            self.finished = True
        return self.rect

    def clear(self) -> None:
        """"""
        self.screen.blit(self.background, self.rect)


def draw_fading(game: "Game", rectlist: list) -> list:
    """"""
    # TODO figure out what fade are for typing
    fade_list = game.fade
    if len(fade_list) != 0:
        for fade in fade_list:
            rectlist.append(fade.update())
    return rectlist


def clear_fading(game: "Game") -> None:
    """"""
    fade_list = game.fade
    if len(fade_list) != 0:
        for fade in fade_list:
            fade.clear()
            if fade.finished:
                fade_list.remove(fade)
