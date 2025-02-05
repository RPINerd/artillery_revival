""""""

import math
import random

import pygame

from .load_save import load_image


def new_ground() -> tuple[dict[int, int], int]:
    """"""
    MIN = 30
    MAX = 330
    angle = float(random.randint(0, 360))

    ground: dict[int, int] = {}
    ground[0] = random.randint(MIN + 70, MAX - 100)
    elevation: float = float(ground[0])
    counter: int = 0
    ajustment: float = 0.0

    max_height = ground[0]

    i = 1
    while i < 800:
        if counter == 0:
            counter = random.randint(5, 40)
            ajustment = float(random.randint(-4, 6))
        if counter < 25:
            angle += ajustment
        if angle >= 360.0:
            angle = 0.0
        elevation += math.cos(math.radians(angle)) * 1.5
        if elevation < MIN:
            angle = 280.0
            counter = random.randint(5, 20)
            ajustment = float(random.randint(1, 3))
        elif elevation > MAX:
            angle = 100.0
            counter = random.randint(5, 20)
            ajustment = float(random.randint(1, 3))
        if (i >= 75 and i <= 125) or (i >= 675 and i <= 725):
            elevation = float(ground[i - 1])
        else:
            elevation += ((random.random() * 4) - 2)
        ground[i] = int(elevation)
        max_height = max(ground[i], max_height)
        counter -= 1
        i += 1
    return ground, max_height


def draw_ground(Game) -> None:
    surface = Game.screen
    ground = Game.ground
    for i in range(0, 800):
        pygame.draw.line(surface, (255, 255, 120), (i, 600 - ground[i]), (i, 599))
        pygame.draw.line(surface, (140, 140, 50), (i, 600 - ground[i]), (i, 600 - ground[i] + 2))
        pygame.draw.line(surface, (200, 200, 80), (i, 600 - ground[i] + 3), (i, 600 - ground[i] + 6))


def draw_mountains(screen: pygame.Surface) -> pygame.Surface:
    """"""
    red = 160.0
    green = 210.0
    blue = 255.0
    LOWERING = 0.9987
    for i in range(0, 200):
        pygame.draw.line(screen, (int(red), int(green), int(blue)), (0, 599 - i), (799, 599 - i))
    for i in range(200, 600):
        pygame.draw.line(screen, (int(red), int(green), int(blue)), (0, 599 - i), (799, 599 - i))
        red *= LOWERING
        green *= LOWERING
        blue *= LOWERING

    MIN = 350
    MAX = 450
    SNOW_MIN = 400
    snow = SNOW_MIN

    if random.randint(0, 2) == 0:
        go_up = True
    else:
        go_up = False
    elevation = random.randint(MIN, MAX)

    for i in range(0, 800):
        pygame.draw.line(screen, (120, 80, 50), (i, 600 - elevation), (i, 599))
        if elevation > SNOW_MIN:
            if random.randint(0, 3) != 0:
                snow = SNOW_MIN + random.randint(-1, 5)
                snow = min(elevation, snow)
            pygame.draw.line(screen, (255, 255, 255), (i, 600 - elevation), (i, 600 - snow))
            pygame.draw.line(screen, (200, 200, 200), (i, 600 - snow + 1), (i, 600 - snow + random.randint(2, 6)))
        if random.randint(0, 2) == 0:
            elevation += 1 if go_up else elevation == elevation - 1
        if elevation == MIN:
            go_up = True
        elif elevation == MAX:
            go_up = False
    return screen.copy()


def update_screen(Game) -> pygame.Surface:
    """"""
    Game.screen.blit(Game.mountains, (0, 0))
    draw_ground(Game)
    return Game.screen.copy()


def generate_trees(Game) -> None:
    """"""
    for y in range(Game.max_height - 15, 0, -2):
        while True:
            x = random.randint(0, 799)
            if y < Game.ground[x]:
                Game.trees.append(Tree(x, (605 - y)))
                break


class Tree(pygame.sprite.Sprite):

    """The tree object"""

    def __init__(self, x: int, y: int) -> None:
        """"""
        pygame.sprite.Sprite.__init__(self)
        self.image: pygame.Surface = None
        self.tree: bool = False

        if random.randint(0, 2) == 0:
            filename = "tree" + str(random.randint(1, 6)) + ".png"
            self.image = load_image(filename, 'sprites/trees', -1)
            self.tree = True
        else:
            filename = "grass" + str(random.randint(1, 4)) + ".png"
            self.image = load_image(filename, 'sprites/trees', -1)
            self.tree = False

        scale = (random.random() / 2) + 0.7
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * scale), int(self.image.get_height() * scale)))
        if random.randint(0, 1) == 0:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect: pygame.Rect = self.image.get_rect(midbottom=(x, y))
        self.damage: int = 0
        self.fallen: bool = False
        self.rotating: bool = False
        self.angle: int = 0
        self.angle_adjustment: int = 0
        self.base_image: pygame.Surface = self.image
        self.base_rect: pygame.Rect = self.rect.copy()

    def update(self, Game) -> None:
        """"""
        if self.damage > 50 or ((self.damage > 1) and not self.tree):
            Game.sprites.remove(self)
        if self.rect.bottom < (599 - Game.ground[self.rect.centerx]):
            self.rect.bottom += 2
            self.base_rect.bottom += 2
            if not self.rotating and not self.fallen:
                self.rotating = True
                self.base_image = self.image
                self.base_rect = self.rect.copy()
                self.width = self.image.get_width()
                self.height = self.image.get_height()
                if random.randint(0, 1) == 0:
                    self.angle_adjustment = 1
                else:
                    self.angle_adjustment = -1
        if self.rotating:
            self.angle += self.angle_adjustment
            if self.angle < 0: self.angle += 360
            elif self.angle > 360: self.angle -= 360
            self.image = pygame.transform.rotate(self.base_image, self.angle)
            sin_angle: float = math.sin(math.radians(self.angle))
            half_height: int = int(self.height / 2)
            self.rect = self.image.get_rect(center=(self.base_rect.centerx - int(sin_angle * (self.width * 3 / 4)), self.base_rect.centery + abs(int(sin_angle * half_height))))
            if (self.angle > 80) and (self.angle < 280):
                self.rotating = False
                self.fallen = True
                self.base_image = self.image
                self.base_rect = self.rect.copy()

    def stain_black(self, shell_x: int, shell_y: int) -> None:
        """"""
        x = shell_x - self.rect.left
        y = shell_y - self.rect.top
        pixel_count = 0
        self.image.lock()
        for i in range(1, 25):
            for angles in range(0, 360, 5):
                # TODO bind this generation within window size
                pixel_x = abs(int(x + math.sin(math.radians(angles)) * i))
                pixel_y = abs(int(y + math.cos(math.radians(angles)) * i))
                if pixel_x > (self.rect.width - 1): continue
                if pixel_y > (self.rect.height - 1): continue
                color = self.image.get_at((pixel_x, pixel_y))
                if color != (255, 125, 255):
                    if random.randint(0, 3) == 0:
                        self.image.set_at((pixel_x, pixel_y), (255, 125, 255))
                    else:
                        self.image.set_at((pixel_x, pixel_y), (0, 0, 0))
                    pixel_count += 1
        self.image.unlock()
        self.damage += int(pixel_count / 10)
        old_rect = self.rect.copy()
        scale_upper: float = int(self.base_image.get_height() * ((200 - float(self.damage)) / 200))
        self.image = pygame.transform.scale(self.base_image, (self.base_image.get_width(), scale_upper))
        self.rect = self.image.get_rect(midbottom=old_rect.midbottom)
