"""
UI Renderer Module
Handles all UI drawing including menus, scores, and game state overlays.
"""

import pygame
from typing import Tuple, List, Dict
from game_objects import Difficulty
from game_config import GameConfig


class UIRenderer:
    """
    Responsible for rendering all UI elements on the screen.
    Includes score display, menus, pause screen, and game over screen.
    """

    def __init__(self, screen: pygame.Surface, config: GameConfig):
        """
        Initialize the UI renderer with screen surface and game configuration.
        Sets up font objects used for different UI text elements.
        """
        self.screen = screen
        self.config = config
        self.fonts: Dict[str, pygame.font.Font] = {}
        self.init_fonts()

    def init_fonts(self) -> None:
        """
        Initialize pygame fonts for various UI elements with configured sizes.
        """
        pygame.font.init()
        self.fonts['score'] = pygame.font.Font(None, self.config.SCORE_FONT_SIZE)
        self.fonts['menu'] = pygame.font.Font(None, self.config.MENU_FONT_SIZE)
        self.fonts['button'] = pygame.font.Font(None, self.config.BUTTON_FONT_SIZE)
        self.fonts['pause'] = pygame.font.Font(None, self.config.PAUSE_FONT_SIZE)

    def update_fonts(self) -> None:
        """
        Update font sizes when screen size or configuration changes.
        """
        self.fonts['score'] = pygame.font.Font(None, self.config.SCORE_FONT_SIZE)
        self.fonts['menu'] = pygame.font.Font(None, self.config.MENU_FONT_SIZE)
        self.fonts['button'] = pygame.font.Font(None, self.config.BUTTON_FONT_SIZE)
        self.fonts['pause'] = pygame.font.Font(None, self.config.PAUSE_FONT_SIZE)

    def draw_center_line(self) -> None:
        """
        Draw the dashed center line dividing the playing field vertically.
        """
        segment_height = int(self.config.SCREEN_HEIGHT * 0.0167)
        gap_height = int(self.config.SCREEN_HEIGHT * 0.0167)
        line_width = int(self.config.SCREEN_WIDTH * 0.005)
        for y in range(0, self.config.SCREEN_HEIGHT, segment_height + gap_height):
            pygame.draw.rect(
                self.screen, self.config.COLOR_CENTER_LINE,
                (self.config.SCREEN_WIDTH // 2 - line_width // 2, y, line_width, segment_height)
            )

    def draw_scores(self, player_score: int, bot_score: int) -> None:
        """
        Draw the current scores of the player and bot near the top center of the screen.
        Uses transparency for style.
        """
        score_surface = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT), pygame.SRCALPHA)
        player_text = self.fonts['score'].render(str(player_score), True, (*self.config.COLOR_WHITE, self.config.SCORE_TRANSPARENCY))
        player_rect = player_text.get_rect()
        player_rect.center = (self.config.SCREEN_WIDTH // 2 - self.config.SCORE_X_OFFSET, self.config.SCORE_Y_POSITION)
        score_surface.blit(player_text, player_rect)

        bot_text = self.fonts['score'].render(str(bot_score), True, (*self.config.COLOR_WHITE, self.config.SCORE_TRANSPARENCY))
        bot_rect = bot_text.get_rect()
        bot_rect.center = (self.config.SCREEN_WIDTH // 2 + self.config.SCORE_X_OFFSET, self.config.SCORE_Y_POSITION)
        score_surface.blit(bot_text, bot_rect)

        self.screen.blit(score_surface, (0, 0))

    def draw_menu(self) -> List[Tuple[pygame.Rect, Difficulty]]:
        """
        Draw the difficulty selection menu with buttons.
        
        Returns:
            List of tuples containing button rectangles and corresponding Difficulty values.
        """
        title_text = self.fonts['menu'].render("Select Difficulty", True, self.config.COLOR_WHITE)
        title_rect = title_text.get_rect(center=(self.config.SCREEN_WIDTH // 2, int(self.config.SCREEN_HEIGHT * 0.25)))
        self.screen.blit(title_text, title_rect)

        difficulties = [Difficulty.VERY_EASY, Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]
        buttons = []
        start_y = int(self.config.SCREEN_HEIGHT * 0.40)

        for i, difficulty in enumerate(difficulties):
            button_y = start_y + i * (self.config.BUTTON_HEIGHT + self.config.BUTTON_SPACING)
            button_rect = pygame.Rect(
                self.config.SCREEN_WIDTH // 2 - self.config.BUTTON_WIDTH // 2,
                button_y,
                self.config.BUTTON_WIDTH,
                self.config.BUTTON_HEIGHT
            )
            pygame.draw.rect(self.screen, self.config.COLOR_WHITE, button_rect, 2)
            button_text = self.fonts['button'].render(difficulty.value, True, self.config.COLOR_WHITE)
            button_text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, button_text_rect)
            buttons.append((button_rect, difficulty))

        return buttons

    def draw_pause_menu(self) -> Dict[str, pygame.Rect]:
        """
        Draw the pause menu overlay with "Resume" and "New Game" buttons.

        Returns:
            Dictionary mapping lowercased button names to their rectangles.
        """
        overlay = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black overlay
        self.screen.blit(overlay, (0, 0))

        title_text = self.fonts['pause'].render("PAUSED", True, self.config.COLOR_WHITE)
        title_rect = title_text.get_rect(center=(self.config.SCREEN_WIDTH // 2, int(self.config.SCREEN_HEIGHT * 0.3)))
        self.screen.blit(title_text, title_rect)

        buttons = {}
        button_labels = ["Resume", "New Game"]
        start_y = int(self.config.SCREEN_HEIGHT * 0.45)

        for i, label in enumerate(button_labels):
            button_y = start_y + i * (self.config.BUTTON_HEIGHT + self.config.BUTTON_SPACING)
            button_rect = pygame.Rect(
                self.config.SCREEN_WIDTH // 2 - self.config.BUTTON_WIDTH // 2,
                button_y,
                self.config.BUTTON_WIDTH,
                self.config.BUTTON_HEIGHT
            )
            pygame.draw.rect(self.screen, self.config.COLOR_WHITE, button_rect, 2)
            button_text = self.fonts['button'].render(label, True, self.config.COLOR_WHITE)
            button_text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, button_text_rect)
            buttons[label.lower().replace(" ", "_")] = button_rect

        return buttons

    def draw_game_over(self, winner: str) -> pygame.Rect:
        """
        Draw the game over screen displaying the winner and a "Play Again" button.

        Args:
            winner: Name of the winning player ("player" or "bot").

        Returns:
            Rectangle for the "Play Again" button.
        """
        winner_text = self.fonts['menu'].render(f"{winner} Wins!", True, self.config.COLOR_WHITE)
        winner_rect = winner_text.get_rect(center=(self.config.SCREEN_WIDTH // 2, int(self.config.SCREEN_HEIGHT * 0.33)))
        self.screen.blit(winner_text, winner_rect)

        button_rect = pygame.Rect(
            self.config.SCREEN_WIDTH // 2 - self.config.BUTTON_WIDTH // 2,
            int(self.config.SCREEN_HEIGHT * 0.5),
            self.config.BUTTON_WIDTH,
            self.config.BUTTON_HEIGHT
        )
        pygame.draw.rect(self.screen, self.config.COLOR_WHITE, button_rect, 2)
        button_text = self.fonts['button'].render("Play Again", True, self.config.COLOR_WHITE)
        button_text_rect = button_text.get_rect(center=button_rect.center)
        self.screen.blit(button_text, button_text_rect)

        return button_rect
