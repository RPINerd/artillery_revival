#!/usr/bin/env python

import pygame
from pygame.locals import *

class Fade_in(object):
    def __init__(self, rect):
        self.rect = rect
        self.screen = pygame.display.get_surface()
        self.image = pygame.Surface(rect.size)
        self.color = 0
        self.image.fill((self.color, self.color, self.color))
        self.finished = False
        self.background = self.image.copy()
        self.background.blit(self.screen, (0,0), rect)
        self.screen.fill((0,0,0), rect)

    def update(self):
        self.color += 5
        self.image.fill((self.color, self.color, self.color))
        self.screen.blit(self.image, self.rect, None, BLEND_RGB_MULT)
        if self.color == 255:
            self.finished = True
        return self.rect

    def clear(self):
        self.screen.blit(self.background, self.rect)

class Fade_out(object):
    def __init__(self, rect):
        self.rect = rect
        self.screen = pygame.display.get_surface()
        self.image = pygame.Surface(rect.size)
        self.color = 255
        self.image.fill((self.color, self.color, self.color))
        self.finished = False
        self.background = self.image.copy()
        self.background.blit(self.screen, (0,0), rect)

    def update(self):
        self.color -= 5
        self.image.fill((self.color, self.color, self.color))
        self.screen.blit(self.image, self.rect, None, BLEND_RGB_MULT)
        if self.color == 0:
            self.finished = True
        return self.rect

    def clear(self):
        self.screen.blit(self.background, self.rect)


def draw_fading(Game, rectlist):
    fade_list = Game.fade
    if len(fade_list) != 0:
        for fade in fade_list:
            rectlist.append(fade.update())
    return rectlist

def clear_fading(Game):
    fade_list = Game.fade
    if len(fade_list) != 0:
        for fade in fade_list:
            fade.clear()
            if fade.finished == True:
                fade_list.remove(fade)


