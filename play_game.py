"""Main entry point for the game."""

from lib.game import Game

if __name__ == "__main__":
    artillery = Game()
    artillery.main_loop()
