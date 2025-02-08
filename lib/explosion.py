""""""

import math
import random
from typing import TYPE_CHECKING

import pygame
from pygame.locals import BLEND_RGB_ADD, BLEND_RGBA_ADD, BLEND_RGBA_SUB, SRCALPHA

from .background import update_screen
from .config import GRAVITY
from .load_save import load_image, load_image_alpha

if TYPE_CHECKING:
    from .game import Game


def explosion(exp_x: int, exp_y: int, game: "Game") -> None:
    """"""
    particles = []
    game.sound.play("explosion_ground")

    game.screen.lock()
    for i in range(1, 17):
        for angles in range(0, 360, 3):
            x = int(exp_x + math.sin(math.radians(angles)) * i)
            y = int(exp_y + math.cos(math.radians(angles)) * i)
            y = min(y, 590)
            if x <= 1:
                x = 0
            elif x >= 798:
                x = 799
            color: pygame.Color = game.screen.get_at((x, y))
            if color != (120, 80, 50, 255):
                game.screen.set_at((x, y), (120, 80, 50))
                if (exp_x - x) == 0:
                    speed_x = (random.random() * 4) - 2
                else:
                    speed_x = (3 / (exp_x - x) * random.random())
                if (exp_y - y) == 0:
                    speed_y = (random.random() * 2) - 1.2
                else:
                    speed_y = (3 / (exp_y - y) * random.random() * 2) - 1
                if random.randint(0, 3) != 0:
                    particle = Particle(color, x, y, speed_x, speed_y)
                    particles.append(particle)
                if y >= (600 - game.ground[x]):
                    game.ground[x] = 599 - y
                while color != (120, 80, 50, 255):
                    y -= 1
                    color = game.screen.get_at((x, y))
                    if random.randint(0, 40) == 0:
                        speed_x = 0.0
                        speed_y = 1.5
                        particle = Particle(color, x, y, speed_x, speed_y)
                        particles.append(particle)
    game.screen.unlock()

    for i in range(-12, -23, -1):
        game.ground[exp_x + i - 1] = game.ground[exp_x + i] + int((game.ground[exp_x + i - 1] - game.ground[exp_x + i]) * 0.35)
    for i in range(12, 23):
        game.ground[exp_x + i + 1] = game.ground[exp_x + i] + int((game.ground[exp_x + i + 1] - game.ground[exp_x + i]) * 0.35)

    game.sprites.add(particles)
    game.sprites.add(Smoke(exp_x, exp_y, True, "ground"))
    game.sprites.add(Smoke(exp_x, exp_y, False, "ground"))
    # flare(exp_x, exp_y, game)
    game.background = update_screen(game)


class Particle(pygame.sprite.Sprite):

    """The particle object"""

    def __init__(self, color: pygame.Color, x: int, y: int, speed_x: float, speed_y: float) -> None:
        """"""
        pygame.sprite.Sprite.__init__(self)
        self.width: int = random.randint(1, 3)
        self.height: int = random.randint(1, 3)
        image: pygame.Surface = pygame.Surface((self.width, self.height))
        image.fill(color)
        self.image: pygame.Surface = image
        self.rect: pygame.Rect = self.image.get_rect()
        self.x: int = x
        self.y: int = y
        self.speed_x: float = speed_x
        self.speed_y: float = speed_y
        self.weight: int = (self.width * self.height * 20) + 20

    def update(self, game: "Game") -> None:
        """"""
        self.x += self.speed_x
        if (int(self.x > 795)) or (int(self.x < 5)):
            game.sprites.remove(self)
        self.y += self.speed_y
        speed_select = 1 if self.speed_x > 0 else -1
        if (599 - game.ground[int(self.x) + speed_select]) < (int(self.y)):
            self.speed_x = (0 - self.speed_x) * 0.15

        if int(self.y) >= (599 - game.ground[int(self.x)]):
            self.speed_y = (0 - self.speed_y) * 0.1
            self.speed_x *= 0.7
            self.y = 599 - game.ground[int(self.x)]

        self.rect.centerx, self.rect.centery = int(self.x), int(self.y)
        self.speed_y = gravity(self.speed_y, self.weight)
        self.speed = math.hypot(self.speed_x, self.speed_y)

        if (self.speed < 0.4) and ((599 - int(self.y)) == game.ground[int(self.x)]):
            game.sprites.remove(self)
            if random.randint(0, 1) == 0:
                if (game.ground[int(self.x) - 1] - game.ground[int(self.x)]) > 1 or (game.ground[int(self.x) + 1] - game.ground[int(self.x)]) > 1:
                    game.ground[int(self.x)] += 1
                elif (game.ground[int(self.x) - 1] - game.ground[int(self.x)]) < -1:
                    game.ground[int(self.x) - 1] += 1
                elif (game.ground[int(self.x) + 1] - game.ground[int(self.x)]) < -1:
                    game.ground[int(self.x) + 1] += 1
                else:
                    game.ground[int(self.x)] += 1
        self.speed_x = apply_wind(self.speed_x, self.weight, game)


class Smoke(pygame.sprite.Sprite):

    """The smoke object"""

    images: dict[int, pygame.Surface] = {}
    images[1] = load_image_alpha('smoke1.png', 'sprites/smoke')
    images[2] = load_image_alpha('smoke2.png', 'sprites/smoke')
    images[3] = load_image_alpha('smoke3.png', 'sprites/smoke')
    images[4] = load_image_alpha('smoke4.png', 'sprites/smoke')
    images[5] = load_image_alpha('smoke5.png', 'sprites/smoke')
    images[6] = load_image_alpha('smoke6.png', 'sprites/smoke')

    def __init__(self, x: int, y: int, rotate_clockwise: bool = True, smoke_type: str | None = None, max_size: int = 130) -> None:
        """"""
        pygame.sprite.Sprite.__init__(self)
        self.image: pygame.Surface = Smoke.images[random.randint(1, 6)].convert_alpha()
        self.rect: pygame.Rect = self.image.get_rect(center=(x, y))
        self.blending_color: pygame.Surface = pygame.Surface((self.image.get_size()), SRCALPHA)
        self.blending_alpha: pygame.Surface = pygame.Surface((self.image.get_size()), SRCALPHA)
        self.angle: int = random.randint(0, 359)
        self.speed_y: float = (random.random() / 15) - 0.1
        self.max_size: int = max_size

        self.blending_color.fill((1, 1, 1, 0))
        self.blending_alpha.fill((0, 0, 0, 1))

        if smoke_type == "ground":
            self.y = y - 5
            if not rotate_clockwise:
                self.angle_adjust = random.random() + 0.4
                self.x = x + random.randint(7, 14)
                self.speed_x = (random.random() / 8) + 0.06
            else:
                self.angle_adjust = random.random() - 1.4
                self.x = x - random.randint(7, 14)
                self.speed_x = (random.random() / 8) - 0.19

        elif smoke_type == "gun":
            self.x = x
            self.y = y
            self.speed_x = 0
            if not rotate_clockwise:
                self.angle_adjust = random.random() + 0.2
            else:
                self.angle_adjust = random.random() - 1.2

        elif smoke_type == "tank":
            self.y = y - 3
            self.speed_y = -1.2
            if not rotate_clockwise:
                self.angle_adjust = random.random() + 1
                self.x = x + random.randint(12, 16)
                self.speed_x = (random.random() / 8) + 0.055
            else:
                self.angle_adjust = random.random() - 2
                self.x = x - random.randint(12, 16)
                self.speed_x = (random.random() / 8) - 0.18

        elif smoke_type == "continuous":
            self.x = x
            self.y = y
            self.speed_x = 0
            self.angle_adjust = 0
            self.speed_y = -0.7

        self.lifespan: float = 1.0
        scale: float = self.lifespan / self.max_size
        self.base_image = self.image
        self.base_image_rect = self.base_image.get_rect()
        scaled_width: int = int(self.base_image_rect.width * scale)
        scaled_height: int = int(self.base_image_rect.height * scale)
        self.image = pygame.transform.scale(self.base_image, (scaled_width, scaled_height))
        self.weight = 30

    def update(self, game: "Game") -> None:
        """"""
        scale: float = self.lifespan / self.max_size
        scaled_width: int = int(self.base_image_rect.width * scale)
        scaled_height: int = int(self.base_image_rect.height * scale)
        self.image = pygame.transform.scale(self.base_image, (scaled_width, scaled_height))
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
        self.speed_x = apply_wind(self.speed_x, self.weight, game)
        self.image = pygame.transform.rotate(self.image, int(self.angle))
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

        if random.randint(0, 4) == 0:
            self.base_image.blit(self.blending_color, (0, 0), None, BLEND_RGBA_ADD)
        self.base_image.blit(self.blending_alpha, (0, 0), None, BLEND_RGBA_SUB)

        self.lifespan += ((100 - self.lifespan) / 40)
        if self.lifespan >= 99.98:
            game.sprites.remove(self)


def flare(x: int, y: int, game: "Game") -> None:
    """"""
    # ! Currently disabled
    image = load_image('flare.png', 'sprites/effects', (0, 0, 0))
    rect = image.get_rect(center=(x, y))
    for tank in game.tanks:
        game.screen.blit(tank.image, tank.rect)
    game.screen.blit(image, rect, None, BLEND_RGB_ADD)
    pygame.display.update(rect)


def gravity(speed_y: int | float, weight: int | float) -> float:
    """"""
    speed_y += weight / GRAVITY
    return min(speed_y, 8.0)


def apply_wind(speed_x: int | float, weight: int | float, game: "Game") -> float:
    """"""
    wind_difference = game.wind - (speed_x * 5)
    air_resistance = 1 - (abs(wind_difference) / weight / 250)
    wind_ajustment = (wind_difference / weight / 60)
    return (speed_x * air_resistance) + wind_ajustment
