"""
Game State Module

Manages different game states and score tracking.
"""

from enum import Enum, auto


class GameState(Enum):
    """Enum for different game states."""
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()


class ScoreManager:
    """Manages player and bot scores."""

    def __init__(self, winning_score: int):
        """
        Initialize the score manager.
        
        Args:
            winning_score: The score required to win the game.
        """
        self.player_score: int = 0
        self.bot_score: int = 0
        self.winning_score: int = winning_score

    def increment_player_score(self) -> None:
        """Increment the player's score by 1."""
        self.player_score += 1

    def increment_bot_score(self) -> None:
        """Increment the bot's score by 1."""
        self.bot_score += 1

    def reset(self) -> None:
        """Reset both scores to 0."""
        self.player_score = 0
        self.bot_score = 0

    def check_winner(self) -> str:
        """
        Check if there is a winner.
        
        Returns:
            "Player" if the player has won.
            "Bot" if the bot has won.
            None if no winner yet.
        """
        if self.player_score >= self.winning_score:
            return "Player"
        elif self.bot_score >= self.winning_score:
            return "Bot"
        return None

    def get_scores(self) -> tuple:
        """
        Get current scores.
        
        Returns:
            Tuple of (player_score, bot_score).
        """
        return self.player_score, self.bot_score
