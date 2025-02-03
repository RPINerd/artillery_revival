#!/usr/bin/env python

import pygame, random, math


def new_ground():
    MIN = 30
    MAX = 330

    angle = float(random.randint(0,360))

    ground = {}
    ground[0] = random.randint(MIN+70, MAX-100)
    elevation = float(ground[0])
    counter = 0
    ajustment = 0.0

    max_height = ground[0]
    
    i = 1
    while i < 800:
        if counter == 0:
            counter = random.randint(5,40)
            ajustment = float(random.randint(-4,6))
        if counter < 25:
            angle = angle + ajustment
        if angle >= 360.0:
            angle = 0.0
        elevation = elevation + math.cos(math.radians(angle))*1.5
        if elevation < MIN:
            angle = 280.0
            counter = random.randint(5,20)
            ajustment = float(random.randint(1,3))
        elif elevation > MAX:
            angle = 100.0
            counter = random.randint(5,20)
            ajustment = float(random.randint(1,3))
        if (i >= 75 and i <= 125) or (i >= 675 and i <= 725):
            elevation = float(ground[i-1])
        else:
            elevation += ((random.random()*4) - 2)
        ground[i] = int(elevation)
        if ground[i] > max_height:
            max_height = ground[i]
        counter -=1
        i += 1
    return ground, max_height


def draw_ground(Game, start=0, end=800):
    surface = Game.screen
    ground = Game.ground
    for i in range(start,end):
        pygame.draw.line(surface, (255, 255, 120), (i, 600-ground[i]), (i, 599))
        pygame.draw.line(surface, (140, 140, 50), (i, 600-ground[i]), (i, 600-ground[i]+2))
        pygame.draw.line(surface, (200, 200, 80), (i, 600-ground[i]+3), (i, 600-ground[i]+6))


def draw_mountains(screen):
    red = 160.0
    green = 210.0
    blue = 255.0
    LOWERING = 0.9987
    for i in range(0,200):
        pygame.draw.line(screen, (int(red), int(green), int(blue)), (0, 599-i), (799, 599-i))
    for i in range(200,600):
        pygame.draw.line(screen, (int(red), int(green), int(blue)), (0, 599-i), (799, 599-i))
        red *= LOWERING
        green *= LOWERING
        blue *= LOWERING
        
    MIN = 350
    MAX = 450
    SNOW_MIN = 400
    snow = SNOW_MIN

    if random.randint(0,2) == 0:
        go_up = True
    else:
        go_up = False
    elevation = random.randint(MIN, MAX)

    for i in range(0,800):
        pygame.draw.line(screen, (120, 80, 50), (i, 600-elevation), (i, 599))
        if elevation > SNOW_MIN:
            if random.randint(0,3) != 0:
                snow = SNOW_MIN + random.randint(-1,5)
                if snow >= elevation: snow = elevation
            pygame.draw.line(screen, (255, 255, 255), (i, 600-elevation), (i, 600-snow))
            pygame.draw.line(screen, (200, 200, 200), (i, 600-snow+1), (i, 600-snow+random.randint(2,6)))
        if random.randint(0,2) == 0:
            if go_up == True: elevation += 1
            else: elevation -= 1
        if elevation == MIN: go_up = True
        elif elevation == MAX: go_up = False

    return screen.copy()    

def update_screen(Game):
    Game.screen.blit(Game.mountains, (0, 0))
    draw_ground(Game)
    return Game.screen.copy()



    
