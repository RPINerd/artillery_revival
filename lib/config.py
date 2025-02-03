"""Global config values for the game."""

# Release info
GAME_NAME: str = "Artillery Duel Revived"
GAME_VER: str = "0.62"

# Display options
SCREEN_SIZE: tuple[int, int] = (800, 600)
FULL_SCREEN: bool = False
COLOR_DEPTH: int = 32
FRAME_SPEED: int = 45

# States
STATE_MENU: str = "Menu"
STATE_INTRO: str = "Intro"
STATE_GAME: str = "Game"
STATE_DAMAGE: str = "Damage"
STATE_END: str = "End"
STATE_QUIT: str = "Quit"

# Mouse
LEFT_BUTTON: int = 1
RIGHT_BUTTON: int = 2

# Misc
GRAVITY: float = 1000.0
