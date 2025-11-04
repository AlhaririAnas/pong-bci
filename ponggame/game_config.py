"""
Game Configuration Module
"""
from typing import Dict, Tuple
from ponggame.game_objects import Difficulty
class GameConfig:
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    MIN_WIDTH = 600
    MIN_HEIGHT = 400
    FPS = 60
    WINDOW_TITLE = "Pong Game"
    COLOR_BACKGROUND = (26, 26, 46)
    COLOR_WHITE = (255, 255, 255)
    COLOR_CENTER_LINE = (68, 68, 68)
    COLOR_SCORE = (255, 255, 255, 51) # 80% transparent
    PADDLE_WIDTH_RATIO = 0.01875
    PADDLE_HEIGHT_RATIO = 0.1667
    PADDLE_OFFSET_RATIO = 0.0375
    PLAYER_SPEED_RATIO = 0.00875
    BALL_RADIUS_RATIO = 0.01
    WINNING_SCORE = 10
    SCORE_FONT_SIZE_RATIO = 0.09
    SCORE_TRANSPARENCY = 51
    SCORE_Y_POSITION_RATIO = 0.167
    SCORE_X_OFFSET_RATIO = 0.125
    BUTTON_WIDTH_RATIO = 0.25
    BUTTON_HEIGHT_RATIO = 0.1
    BUTTON_SPACING_RATIO = 0.05
    MENU_FONT_SIZE_RATIO = 0.06
    BUTTON_FONT_SIZE_RATIO = 0.04
    PAUSE_FONT_SIZE_RATIO = 0.08
    RESET_DELAY_MS = 2000
    DIFFICULTY_SETTINGS: Dict[Difficulty, Dict[str, float]] = {
        Difficulty.VERY_EASY: {
            'ball_speed': 2.2,
            'bot_speed': 1.5
        },
        Difficulty.EASY: {
            'ball_speed': 3.5,
            'bot_speed': 2.2
        },
        Difficulty.MEDIUM: {
            'ball_speed': 6.0,
            'bot_speed': 4.0
        },
        Difficulty.HARD: {
            'ball_speed': 8.4,
            'bot_speed': 6.5
        }
    }
    def __init__(self, width: int = 800, height: int = 600):
        self.update_screen_size(width, height)
    def update_screen_size(self, width: int, height: int) -> None:
        self.SCREEN_WIDTH = max(width, self.MIN_WIDTH)
        self.SCREEN_HEIGHT = max(height, self.MIN_HEIGHT)
        self.PADDLE_WIDTH = int(self.SCREEN_WIDTH * self.PADDLE_WIDTH_RATIO)
        self.PADDLE_HEIGHT = int(self.SCREEN_HEIGHT * self.PADDLE_HEIGHT_RATIO)
        self.PADDLE_OFFSET = int(self.SCREEN_WIDTH * self.PADDLE_OFFSET_RATIO)
        self.PLAYER_SPEED = self.SCREEN_WIDTH * self.PLAYER_SPEED_RATIO
        self.BALL_RADIUS = int(self.SCREEN_WIDTH * self.BALL_RADIUS_RATIO)
        self.SCORE_FONT_SIZE = int(self.SCREEN_WIDTH * self.SCORE_FONT_SIZE_RATIO)
        self.SCORE_Y_POSITION = int(self.SCREEN_HEIGHT * self.SCORE_Y_POSITION_RATIO)
        self.SCORE_X_OFFSET = int(self.SCREEN_WIDTH * self.SCORE_X_OFFSET_RATIO)
        self.BUTTON_WIDTH = int(self.SCREEN_WIDTH * self.BUTTON_WIDTH_RATIO)
        self.BUTTON_HEIGHT = int(self.SCREEN_HEIGHT * self.BUTTON_HEIGHT_RATIO)
        self.BUTTON_SPACING = int(self.SCREEN_HEIGHT * self.BUTTON_SPACING_RATIO)
        self.MENU_FONT_SIZE = int(self.SCREEN_WIDTH * self.MENU_FONT_SIZE_RATIO)
        self.BUTTON_FONT_SIZE = int(self.SCREEN_WIDTH * self.BUTTON_FONT_SIZE_RATIO)
        self.PAUSE_FONT_SIZE = int(self.SCREEN_WIDTH * self.PAUSE_FONT_SIZE_RATIO)
    def get_difficulty_settings(self, difficulty: Difficulty) -> Dict[str, float]:
        return self.DIFFICULTY_SETTINGS.get(difficulty, self.DIFFICULTY_SETTINGS[Difficulty.EASY])
    def scale_speed(self, base_speed: float) -> float:
        scale_factor = self.SCREEN_WIDTH / 800.0
        return base_speed * scale_factor
