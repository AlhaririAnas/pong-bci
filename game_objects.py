"""
Game Objects Module
Contains all game object classes for the Pong game.
"""

import pygame
import random
from typing import Tuple
from enum import Enum


class Difficulty(Enum):
    """
    Enum representing different bot difficulty levels.
    Each level changes bot accuracy, reaction time, and smoothness.
    """
    VERY_EASY = "Very Easy"
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class GameObject:
    """
    Base class for all game objects.
    Stores position, size, and color, and requires a draw method.
    """
    def __init__(self, x: float, y: float, width: float, height: float, color: Tuple[int, int, int]):
        # Object position and size
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def draw(self, screen: pygame.Surface) -> None:
        """
        Abstract draw method to be implemented by subclasses.
        """
        raise NotImplementedError


class Paddle(GameObject):
    """
    Class representing a player's or bot's paddle.
    Handles movement, collision boundaries, and rendering.
    """
    def __init__(self, x: float, y: float, width: float, height: float, color: Tuple[int, int, int], speed: float):
        super().__init__(x, y, width, height, color)
        self.speed = speed
        self.velocity = 0
        self.target_y = y

    def move(self, direction: int, screen_height: int) -> None:
        """
        Move the paddle up or down based on input direction.
        Keeps the paddle within screen boundaries.
        """
        self.velocity = direction * self.speed
        self.y += self.velocity

        # Prevent paddle from moving outside the screen
        if self.y < 0:
            self.y = 0
        elif self.y + self.height > screen_height:
            self.y = screen_height - self.height

    def smooth_move_to(self, target_y: float, smoothing: float, screen_height: int) -> None:
        """
        Move smoothly to a target vertical position (used for AI control).
        """
        self.target_y = target_y
        diff = self.target_y - self.y
        self.y += diff * smoothing

        # Boundary check
        if self.y < 0:
            self.y = 0
        elif self.y + self.height > screen_height:
            self.y = screen_height - self.height

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the paddle on the screen.
        """
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def get_rect(self) -> pygame.Rect:
        """
        Return a pygame.Rect representing the paddle for collision detection.
        """
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Ball(GameObject):
    """
    Class representing the ball.
    Handles movement, bouncing, resetting, and collision detection.
    """
    def __init__(self, x: float, y: float, radius: float, color: Tuple[int, int, int], speed: float):
        super().__init__(x, y, radius * 2, radius * 2, color)
        self.radius = radius
        self.base_speed = speed
        self.velocity_x = 0
        self.velocity_y = 0
        self.initial_x = x
        self.initial_y = y

    def reset_position(self, direction: int = 0, target_y: float = None) -> None:
        """
        Reset the ball to the initial position and set a new random or directed velocity.
        """
        self.x = self.initial_x
        self.y = self.initial_y

        # Choose a direction if none given
        if direction == 0:
            direction = random.choice([-1, 1])

        self.velocity_x = self.base_speed * direction

        # If a target is given, aim towards it
        if target_y is not None:
            y_diff = target_y - self.y
            self.velocity_y = (y_diff / abs(self.initial_x - (0 if direction < 0 else self.initial_x * 2))) * self.base_speed * 0.6
        else:
            # Random vertical speed
            self.velocity_y = self.base_speed * random.choice([-1, 1]) * random.uniform(0.5, 1.0)

    def move(self, screen_width: int, screen_height: int) -> None:
        """
        Update ball position. Bounce off top and bottom walls.
        """
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Bounce when hitting top or bottom
        if self.y - self.radius <= 0 or self.y + self.radius >= screen_height:
            self.velocity_y *= -1
            if self.y - self.radius <= 0:
                self.y = self.radius
            else:
                self.y = screen_height - self.radius

    def bounce_off_paddle(self, paddle: Paddle) -> None:
        """
        Reflect the ball horizontally when it hits a paddle.
        Adjust vertical angle based on hit position.
        """
        self.velocity_x *= -1
        paddle_center = paddle.y + paddle.height / 2
        hit_pos = (self.y - paddle_center) / (paddle.height / 2)
        self.velocity_y = hit_pos * self.base_speed * 0.8

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the ball on the screen.
        """
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def check_paddle_collision(self, paddle: Paddle) -> bool:
        """
        Check collision between ball and paddle using rectangle overlap.
        Returns True if colliding.
        """
        ball_rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
        return ball_rect.colliderect(paddle.get_rect())