""""""


from pathlib import Path
from typing import TYPE_CHECKING

import pygame

from .config import GAME_NAME, GAME_VER, STATE_QUIT

if TYPE_CHECKING:
    from .game import Game


class Menu:

    """The main game menu screen"""

    def __init__(self, game: "Game") -> None:
        """"""
        self.screen = game.screen
        self.game_started = game.game_started
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

    def draw(self) -> None:
        """"""
        # TODO sort out the mess of text rendering
        self.screen.fill((0, 0, 0))
        title = self.title_font.render(GAME_NAME, True, (180, 180, 0))
        self.screen.blit(title, ((self.screen.get_width() / 2) - (title.get_width() / 2), 80))
        version = self.version_font.render("Version : " + GAME_VER, True, (185, 185, 185))
        self.screen.blit(version, (self.screen.get_width() - version.get_width() - 5, self.screen.get_height() - version.get_height() - 5))

        if self.new_game_selected:
            if self.players_selected:
                pygame.draw.rect(self.screen, (180, 180, 0), self.private_rect, 3)
                pygame.draw.rect(self.screen, (180, 180, 0), self.captain_rect, 3)
                pygame.draw.rect(self.screen, (180, 180, 0), self.general_rect, 3)
                text = self.font.render("Private", True, (200, 200, 200))
                text_halfheight = text.get_height() / 2
                text_halfwidth = text.get_width() / 2
                self.screen.blit(text, (self.private_rect.centerx - text_halfwidth, self.private_rect.centery - text_halfheight))
                text = self.font.render("Captain", True, (200, 200, 200))
                self.screen.blit(text, (self.captain_rect.centerx - text_halfwidth, self.captain_rect.centery - text_halfheight))
                text = self.font.render("General", True, (200, 200, 200))
                self.screen.blit(text, (self.general_rect.centerx - text_halfwidth, self.general_rect.centery - text_halfheight))
            else:
                pygame.draw.rect(self.screen, (180, 180, 0), self.player1_rect, 3)
                pygame.draw.rect(self.screen, (180, 180, 0), self.player2_rect, 3)
                text = self.font.render("1 player", True, (200, 200, 200))
                text_halfheight = text.get_height() / 2
                text_halfwidth = text.get_width() / 2
                self.screen.blit(text, (self.player1_rect.centerx - text_halfwidth, self.player1_rect.centery - text_halfheight))
                text = self.font.render("2 players", True, (200, 200, 200))
                text_halfheight = text.get_height() / 2
                text_halfwidth = text.get_width() / 2
                self.screen.blit(text, (self.player2_rect.centerx - text_halfwidth, self.player2_rect.centery - text_halfheight))
        else:
            pygame.draw.rect(self.screen, (180, 180, 0), self.new_game_rect, 3)
            pygame.draw.rect(self.screen, (180, 180, 0), self.quit_rect, 3)
            if self.game_started:
                text = self.font.render("Return to game", True, (200, 200, 200))
            else:
                text = self.font.render("New game", True, (200, 200, 200))
            text_halfheight = text.get_height() / 2
            text_halfwidth = text.get_width() / 2
            self.screen.blit(text, (self.new_game_rect.centerx - text_halfwidth, self.new_game_rect.centery - text_halfheight))
            text = self.font.render("Quit", True, (200, 200, 200))
            text_halfheight = text.get_height() / 2
            text_halfwidth = text.get_width() / 2
            self.screen.blit(text, (self.quit_rect.centerx - text_halfwidth, self.quit_rect.centery - text_halfheight))

    def check_mouse_event(self, game: "Game", pos: tuple[int, int]) -> None:
        """"""
        if not self.new_game_selected:
            if self.new_game_rect.collidepoint(pos):
                self.new_game_selected = True
                self.update_screen = True
                game.fade = []
            elif self.quit_rect.collidepoint(pos):
                game.state = STATE_QUIT
        elif not self.players_selected:
            if self.player1_rect.collidepoint(pos):
                self.players_selected = True
                game.number_players = 1
                self.update_screen = True
            elif self.player2_rect.collidepoint(pos):
                self.players_selected = True
                game.number_players = 2
                self.update_screen = True
        elif not self.difficulty_selected:
            if self.private_rect.collidepoint(pos):
                self.difficulty_selected = True
                game.difficulty = 1
                game.start_game = True
            elif self.captain_rect.collidepoint(pos):
                self.difficulty_selected = True
                game.difficulty = 2
                game.start_game = True
            elif self.general_rect.collidepoint(pos):
                self.difficulty_selected = True
                game.difficulty = 3
                game.start_game = True

        if game.start_game:
            self.new_game_selected = False
            self.players_selected = False
            self.difficulty_selected = False
