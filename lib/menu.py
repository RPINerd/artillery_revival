#!/usr/bin/env python


from pathlib import Path

import pygame

from .config import GAME_NAME, GAME_VER, STATE_QUIT


class Menu:

    """The main game menu screen"""

    def __init__(self, Game):
        self.screen = Game.screen
        self.game_started = Game.game_started
        self.update_screen = False

        self.player1_rect = pygame.Rect(300, 250, 200, 50)
        self.player2_rect = pygame.Rect(300, 350, 200, 50)
        self.new_game_rect = pygame.Rect(250, 250, 300, 50)
        self.quit_rect = pygame.Rect(250, 350, 300, 50)
        self.private_rect = pygame.Rect(300, 250, 200, 50)
        self.captain_rect = pygame.Rect(300, 350, 200, 50)
        self.general_rect = pygame.Rect(300, 450, 200, 50)
        self.update_buttons_rect = pygame.Rect(0, 150, 800, 400)

        self.new_game_selected = False
        self.players_selected = False
        self.difficulty_selected = False

        self.title_font = pygame.font.Font(Path.joinpath(Path.cwd(), 'data', 'misc', 'COOPBL.ttf'), 50)
        self.font = pygame.font.Font(Path.joinpath(Path.cwd(), 'data', 'misc', 'COOPBL.ttf'), 30)
        self.version_font = pygame.font.Font(Path.joinpath(Path.cwd(), 'data', 'misc', 'COOPBL.ttf'), 14)

    def draw(self):
        self.screen.fill((0, 0, 0))
        title = self.title_font.render(GAME_NAME, True, (180, 180, 0))
        self.screen.blit(title, ((self.screen.get_width() / 2) - (title.get_width() / 2), 80))
        version = self.version_font.render("Version : " + GAME_VER, True, (185, 185, 185))
        self.screen.blit(version, (self.screen.get_width() - version.get_width() - 5, self.screen.get_height() - version.get_height() - 5))

        if self.new_game_selected == True:
            if self.players_selected == True:
                pygame.draw.rect(self.screen, (180, 180, 0), self.private_rect, 3)
                pygame.draw.rect(self.screen, (180, 180, 0), self.captain_rect, 3)
                pygame.draw.rect(self.screen, (180, 180, 0), self.general_rect, 3)
                text = self.font.render("Private", True, (200, 200, 200))
                self.screen.blit(text, (self.private_rect.centerx - (text.get_width() / 2), self.private_rect.centery - (text.get_height() / 2)))
                text = self.font.render("Captain", True, (200, 200, 200))
                self.screen.blit(text, (self.captain_rect.centerx - (text.get_width() / 2), self.captain_rect.centery - (text.get_height() / 2)))
                text = self.font.render("General", True, (200, 200, 200))
                self.screen.blit(text, (self.general_rect.centerx - (text.get_width() / 2), self.general_rect.centery - (text.get_height() / 2)))
            else:
                pygame.draw.rect(self.screen, (180, 180, 0), self.player1_rect, 3)
                pygame.draw.rect(self.screen, (180, 180, 0), self.player2_rect, 3)
                text = self.font.render("1 player", True, (200, 200, 200))
                self.screen.blit(text, (self.player1_rect.centerx - (text.get_width() / 2), self.player1_rect.centery - (text.get_height() / 2)))
                text = self.font.render("2 players", True, (200, 200, 200))
                self.screen.blit(text, (self.player2_rect.centerx - (text.get_width() / 2), self.player2_rect.centery - (text.get_height() / 2)))
        else:
            pygame.draw.rect(self.screen, (180, 180, 0), self.new_game_rect, 3)
            pygame.draw.rect(self.screen, (180, 180, 0), self.quit_rect, 3)
            if self.game_started == True:
                text = self.font.render("Return to game", True, (200, 200, 200))
            else:
                text = self.font.render("New game", True, (200, 200, 200))
            self.screen.blit(text, (self.new_game_rect.centerx - (text.get_width() / 2), self.new_game_rect.centery - (text.get_height() / 2)))
            text = self.font.render("Quit", True, (200, 200, 200))
            self.screen.blit(text, (self.quit_rect.centerx - (text.get_width() / 2), self.quit_rect.centery - (text.get_height() / 2)))

    def check_mouse_event(self, Game, pos):
        if self.new_game_selected == False:
            if self.new_game_rect.collidepoint(pos) == True:
                self.new_game_selected = True
                self.update_screen = True
                Game.fade = []
            elif self.quit_rect.collidepoint(pos) == True:
                Game.state = STATE_QUIT
        elif self.players_selected == False:
            if self.player1_rect.collidepoint(pos) == True:
                self.players_selected = True
                Game.number_players = 1
                self.update_screen = True
            elif self.player2_rect.collidepoint(pos) == True:
                self.players_selected = True
                Game.number_players = 2
                self.update_screen = True
        elif self.difficulty_selected == False:
            if self.private_rect.collidepoint(pos) == True:
                self.difficulty_selected = True
                Game.difficulty = 1
                Game.start_game = True
            elif self.captain_rect.collidepoint(pos) == True:
                self.difficulty_selected = True
                Game.difficulty = 2
                Game.start_game = True
            elif self.general_rect.collidepoint(pos) == True:
                self.difficulty_selected = True
                Game.difficulty = 3
                Game.start_game = True

        if Game.start_game == True:
            self.new_game_selected = False
            self.players_selected = False
            self.difficulty_selected = False
