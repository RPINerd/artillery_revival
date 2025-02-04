#!/usr/bin/env python

from pathlib import Path

import pygame
from pygame.locals import RLEACCEL


def load_image(image_name, path, colorkey=None):
    fullname = Path.joinpath(Path.cwd(), 'data', str(path), image_name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print("Cannot load image:", image_name)
        raise SystemExit(message)
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image.convert()


def load_image_alpha(image_name, path):
    fullname = Path.joinpath(Path.cwd(), 'data', str(path), image_name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print("Cannot load image:", image_name)
        raise SystemExit(message)
    return image


def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = Path.joinpath(Path.cwd(), 'data', 'sound', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error as message:
        print("Cannot load sound:", fullname)
        raise SystemExit(message)
    return sound


def load_music(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = Path.joinpath(Path.cwd(), 'data', 'sound', name)
    try:
        music = pygame.mixer.music.load(fullname)
    except pygame.error as message:
        print("Cannot load music:", fullname)
        raise SystemExit(message)
    return music
