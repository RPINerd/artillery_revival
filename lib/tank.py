""""""

import math
from typing import TYPE_CHECKING, Union

import pygame

from .explosion import apply_wind, explosion, gravity
from .load_save import load_image

if TYPE_CHECKING:
    from .background import Tree
    from .game import Game

TANK_HEALTH = 100
VERTICAL = 90


class Gun(pygame.sprite.Sprite):

    """The Gun object"""

    image = None

    def __init__(self, position: str, game: "Game") -> None:
        """"""
        pygame.sprite.Sprite.__init__(self)
        if Gun.image is None:
            Gun.image = load_image('gun.png', 'sprites', -1)
        self.image = Gun.image
        self.rect = self.image.get_rect()
        self.position = position
        self.ground = game.ground
        self.angle = 00
        self.powder = 40
        if self.position == "left":
            self.rect.center = (122, 584 - self.ground[80])
        elif self.position == "right":
            self.rect.center = (680, 584 - self.ground[680])
            self.image = pygame.transform.flip(self.image, 1, 0)
        self.base_image = self.image

    def turn(self, adjustment: int) -> None:
        """"""
        self.angle += adjustment
        if self.angle > VERTICAL:
            self.angle = VERTICAL
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

    def update(self, game: "Game") -> None:
        """"""
        pass


class Tank(pygame.sprite.Sprite):

    """The tank object"""

    def __init__(self, position: str, gun: Gun, game: "Game") -> None:
        """"""
        pygame.sprite.Sprite.__init__(self)
        self.image: pygame.Surface = load_image('tank.png', 'sprites', -1)
        self.rect: pygame.Rect = self.image.get_rect()
        self.ground: list = game.ground
        self.position: str = position
        self.time_to_fire: int = 14
        self.damage: int = 0
        self.damaged: bool = False
        self.gun: Gun = gun

        # self.intro_image = Tank.image.copy()
        # self.intro_image.blit(load_image('gun.png', 'sprites', -1), (38,4))
        # self.base_intro_image = self.intro_image

        if self.position == "left":
            self.rect.bottomleft = (71, 600 - self.ground[81])
        elif self.position == "right":
            self.rect.bottomleft = (671, 600 - self.ground[681])
            self.image = pygame.transform.flip(self.image, 1, 0)
            # self.intro_image = pygame.transform.flip(self.intro_image, 1, 0)
        self.base_image = self.image

    def update(self, game: "Game") -> None:
        """"""
        pass

    def stain_black(self, shell_x: int, shell_y: int) -> None:
        """"""
        x = shell_x - self.rect.left
        y = shell_y - self.rect.top
        pixel_count = 0
        self.image.lock()
        for i in range(1, 20):
            for angles in range(0, 360, 6):
                # TODO bind this within the image rect
                pixel_x = abs(int(x + math.sin(math.radians(angles)) * i))
                pixel_y = abs(int(y + math.cos(math.radians(angles)) * i))
                if pixel_x > (self.rect.width - 1):
                    continue
                if pixel_y > (self.rect.height - 1):
                    continue
                color = self.image.get_at((pixel_x, pixel_y))
                if color != (255, 125, 255):
                    self.image.set_at((pixel_x, pixel_y), (int(color[0] * 0.6), int(color[1] * 0.6), int(color[2] * 0.6)))
                    pixel_count += 1
        self.image.unlock()
        self.damage += int(pixel_count / 10)
        self.damaged = True

    def intro(self, x: int, ground: dict[int, int]) -> None:
        """"""
        pass


class Shell(pygame.sprite.Sprite):

    """The Shell object"""

    image = None

    def __init__(self, tank: Tank) -> None:
        """"""
        pygame.sprite.Sprite.__init__(self)
        if Shell.image is None:
            Shell.image = load_image('shell.png', 'sprites', -1)
        self.image = Shell.image
        self.rect = self.image.get_rect()
        self.from_tank = tank
        self.target = tank.ennemy
        if tank.position == "left":
            self.rect.center = tank.gun.rect.topright
            self.speed_x = math.sin(math.radians(90 - tank.gun.angle)) * (float(tank.gun.powder + 5) / 9)
            self.speed_y = (0 - math.cos(math.radians(90 - tank.gun.angle))) * (float(tank.gun.powder + 5) / 9)
        elif tank.position == "right":
            self.rect.center = tank.gun.rect.topleft
            self.speed_x = (0 - math.sin(math.radians(90 - tank.gun.angle))) * (float(tank.gun.powder + 5) / 9)
            self.speed_y = (0 - math.cos(math.radians(90 - tank.gun.angle))) * (float(tank.gun.powder + 5) / 9)
        self.pos_x = self.rect.centerx
        self.pos_y = self.rect.centery
        self.weight = 55

    def update(self, game: "Game") -> None:
        """"""
        self.pos_x += self.speed_x
        if (self.pos_x >= 779) or (self.pos_x <= 21):
            game.sprites.remove(self)
            game.change_turn()
        self.pos_y += self.speed_y
        if (self.pos_y >= 590):
            game.sprites.remove(self)
            game.change_turn()
        self.rect.centerx, self.rect.centery = int(self.pos_x), int(self.pos_y)
        self.speed_y = gravity(self.speed_y, self.weight)
        self.speed_x = apply_wind(self.speed_x, self.weight, game)

        for collide in pygame.sprite.spritecollide(self, game.sprites, 0):
            if collide in (self.from_tank, self.target) or collide in game.trees:
                if self.confirm_collision(collide):
                    self.explode(game, collide)
                    break

        if int(self.pos_y) >= (598 - game.ground[int(self.pos_x)]):
            self.explode(game)

    def explode(self, game: "Game", collide: Union[Tank, "Tree", None] = None) -> None:
        """"""
        if collide is not None:
            print(type(collide))
            collide.stain_black(self.pos_x, self.pos_y)
            game.screen.blit(collide.image, collide.rect)
        explosion(int(self.pos_x), int(self.pos_y), game)
        game.sprites.remove(self)
        game.change_turn()

    def confirm_collision(self, target: Union[Tank, "Tree"]) -> bool:
        """"""
        print(type(target))
        if target.rect.collidepoint(int(self.pos_x), int(self.pos_y)):
            adjusted_x = int(self.pos_x) - target.rect.left
            adjusted_y = int(self.pos_y) - target.rect.top
            return target.image.get_at((adjusted_x, adjusted_y)) != target.image.get_colorkey()
        return False
