#!/usr/bin/env python

import pygame
from load_save import load_sound


class Sound(object):
    """ Sound Mixer """
    def __init__(self):
        self.sounds = {}
        self.sounds["gun"] = load_sound('gun.wav')
        self.sounds["explosion"] = load_sound('explosion.wav')
        self.sounds["explosion_tank"] = load_sound('bigboom.wav')

    def play(self, key):
        sound = self.sounds[key]
        sound.play()
