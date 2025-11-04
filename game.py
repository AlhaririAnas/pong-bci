"""
Game Module
Enthält die Hauptspiel-Logik und Game Loop.
"""

import pygame
import sys
from typing import Optional, List, Tuple, Dict

from game_objects import Paddle, Ball, BotController, Difficulty
from game_config import GameConfig
from game_state import GameState, ScoreManager
from ui_renderer import UIRenderer


class PongGame:
    """Hauptspiel-Klasse die alle Komponenten koordiniert."""

    def __init__(self):
        # Pygame initialisieren
        pygame.init()

        # Konfiguration laden
        self.config = GameConfig()

        # Display einrichten (resizable)
        self.screen = pygame.display.set_mode(
            (self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT),
            pygame.RESIZABLE
        )
        pygame.display.set_caption(self.config.WINDOW_TITLE)

        # Clock für FPS
        self.clock = pygame.time.Clock()

        # UI Renderer
        self.ui_renderer = UIRenderer(self.screen, self.config)

        # Game State
        self.state = GameState.MENU
        self.score_manager = ScoreManager(self.config.WINNING_SCORE)

        # Spielobjekte (werden später initialisiert)
        self.player_paddle: Optional[Paddle] = None
        self.bot_paddle: Optional[Paddle] = None
        self.ball: Optional[Ball] = None
        self.bot_controller: Optional[BotController] = None

        # Input State
        self.keys_pressed = set()

        # Difficulty
        self.current_difficulty: Optional[Difficulty] = None

        # UI Elements
        self.menu_buttons: List[Tuple[pygame.Rect, Difficulty]] = []
        self.pause_buttons: Dict[str, pygame.Rect] = {}
        self.play_again_button: Optional[pygame.Rect] = None
        self.winner: Optional[str] = None

        # Reset Timer
        self.reset_timer = 0
        self.waiting_for_reset = False
        self.last_scorer = None  # "player" oder "bot"

    def initialize_game_objects(self, difficulty: Difficulty) -> None:
        """
        Initialisiert alle Spielobjekte basierend auf Schwierigkeit.

        Args:
            difficulty: Gewählter Schwierigkeitsgrad
        """
        self.current_difficulty = difficulty
        settings = self.config.get_difficulty_settings(difficulty)

        # Skaliere Geschwindigkeiten
        ball_speed = self.config.scale_speed(settings['ball_speed'])
        bot_speed = self.config.scale_speed(settings['bot_speed'])

        # Player Paddle (links)
        self.player_paddle = Paddle(
            x=self.config.PADDLE_OFFSET,
            y=self.config.SCREEN_HEIGHT // 2 - self.config.PADDLE_HEIGHT // 2,
            width=self.config.PADDLE_WIDTH,
            height=self.config.PADDLE_HEIGHT,
            color=self.config.COLOR_WHITE,
            speed=self.config.PLAYER_SPEED
        )

        # Bot Paddle (rechts)
        self.bot_paddle = Paddle(
            x=self.config.SCREEN_WIDTH - self.config.PADDLE_OFFSET - self.config.PADDLE_WIDTH,
            y=self.config.SCREEN_HEIGHT // 2 - self.config.PADDLE_HEIGHT // 2,
            width=self.config.PADDLE_WIDTH,
            height=self.config.PADDLE_HEIGHT,
            color=self.config.COLOR_WHITE,
            speed=bot_speed
        )

        # Ball
        self.ball = Ball(
            x=self.config.SCREEN_WIDTH // 2,
            y=self.config.SCREEN_HEIGHT // 2,
            radius=self.config.BALL_RADIUS,
            color=self.config.COLOR_WHITE,
            speed=ball_speed
        )
        self.ball.reset_position(0)  # Random Richtung zu Beginn

        # Bot Controller
        self.bot_controller = BotController(difficulty)

        # Score zurücksetzen
        self.score_manager.reset()

        # Reset state
        self.waiting_for_reset = False
        self.reset_timer = 0
        self.last_scorer = None

    def resize_game_objects(self) -> None:
        """Passt alle Spielobjekte an neue Fenstergröße an."""
        if not self.player_paddle or not self.bot_paddle or not self.ball:
            return

        # Berechne relative Positionen
        player_y_ratio = self.player_paddle.y / self.screen.get_height()
        bot_y_ratio = self.bot_paddle.y / self.screen.get_height()
        ball_x_ratio = self.ball.x / self.screen.get_width()
        ball_y_ratio = self.ball.y / self.screen.get_height()

        # Hole neue Einstellungen
        settings = self.config.get_difficulty_settings(self.current_difficulty)
        ball_speed = self.config.scale_speed(settings['ball_speed'])
        bot_speed = self.config.scale_speed(settings['bot_speed'])

        # Update Player Paddle
        self.player_paddle.x = self.config.PADDLE_OFFSET
        self.player_paddle.y = player_y_ratio * self.config.SCREEN_HEIGHT
        self.player_paddle.width = self.config.PADDLE_WIDTH
        self.player_paddle.height = self.config.PADDLE_HEIGHT
        self.player_paddle.speed = self.config.PLAYER_SPEED

        # Update Bot Paddle
        self.bot_paddle.x = self.config.SCREEN_WIDTH - self.config.PADDLE_OFFSET - self.config.PADDLE_WIDTH
        self.bot_paddle.y = bot_y_ratio * self.config.SCREEN_HEIGHT
        self.bot_paddle.width = self.config.PADDLE_WIDTH
        self.bot_paddle.height = self.config.PADDLE_HEIGHT
        self.bot_paddle.speed = bot_speed

        # Update Ball
        self.ball.x = ball_x_ratio * self.config.SCREEN_WIDTH
        self.ball.y = ball_y_ratio * self.config.SCREEN_HEIGHT
        self.ball.radius = self.config.BALL_RADIUS
        self.ball.initial_x = self.config.SCREEN_WIDTH // 2
        self.ball.initial_y = self.config.SCREEN_HEIGHT // 2
        self.ball.base_speed = ball_speed

        # Skaliere aktuelle Geschwindigkeiten
        speed_ratio = ball_speed / settings['ball_speed']
        self.ball.velocity_x *= speed_ratio
        self.ball.velocity_y *= speed_ratio

    def handle_input(self) -> bool:
        """
        Verarbeitet alle Input-Events.

        Returns:
            False wenn das Spiel beendet werden soll, sonst True
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # Window Resize
            if event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode(
                    (event.w, event.h), 
                    pygame.RESIZABLE
                )
                self.config.update_screen_size(event.w, event.h)
                self.ui_renderer.update_fonts()

                # Resize game objects wenn im Spiel
                if self.state == GameState.PLAYING and self.player_paddle:
                    self.resize_game_objects()

            # Menu State
            if self.state == GameState.MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    for button_rect, difficulty in self.menu_buttons:
                        if button_rect.collidepoint(mouse_pos):
                            self.initialize_game_objects(difficulty)
                            self.state = GameState.PLAYING
                            break

            # Pause State
            elif self.state == GameState.PAUSED:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if 'resume' in self.pause_buttons and self.pause_buttons['resume'].collidepoint(mouse_pos):
                        self.state = GameState.PLAYING
                    elif 'new_game' in self.pause_buttons and self.pause_buttons['new_game'].collidepoint(mouse_pos):
                        self.state = GameState.MENU

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PLAYING

            # Game Over State
            elif self.state == GameState.GAME_OVER:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.play_again_button and self.play_again_button.collidepoint(mouse_pos):
                        self.state = GameState.MENU

            # Playing State
            elif self.state == GameState.PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_w, pygame.K_UP):
                        self.keys_pressed.add('up')
                    elif event.key in (pygame.K_s, pygame.K_DOWN):
                        self.keys_pressed.add('down')
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.PAUSED

                elif event.type == pygame.KEYUP:
                    if event.key in (pygame.K_w, pygame.K_UP):
                        self.keys_pressed.discard('up')
                    elif event.key in (pygame.K_s, pygame.K_DOWN):
                        self.keys_pressed.discard('down')

        return True

    def update(self) -> None:
        """Aktualisiert den Spielzustand."""
        if self.state != GameState.PLAYING:
            return

        # Wenn wir auf Reset warten
        if self.waiting_for_reset:
            current_time = pygame.time.get_ticks()
            if current_time - self.reset_timer >= self.config.RESET_DELAY_MS:
                # Reset Ball - Verlierer sendet zur aktuellen Paddle-Position
                if self.last_scorer == "bot":
                    # Player hat verloren, Ball fliegt zu Player-Paddle
                    direction = -1
                    target_y = self.player_paddle.y + self.player_paddle.height / 2
                else:
                    # Bot hat verloren, Ball fliegt zu Bot-Paddle
                    direction = 1
                    target_y = self.bot_paddle.y + self.bot_paddle.height / 2

                self.ball.reset_position(direction, target_y)
                self.waiting_for_reset = False
            return

        # Player Paddle Bewegung
        direction = 0
        if 'up' in self.keys_pressed:
            direction = -1
        elif 'down' in self.keys_pressed:
            direction = 1
        self.player_paddle.move(direction, self.config.SCREEN_HEIGHT)

        # Bot Paddle Bewegung
        self.bot_controller.update(self.bot_paddle, self.ball, self.config.SCREEN_HEIGHT)

        # Ball Bewegung
        self.ball.move(self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT)

        # Paddle-Kollisionen
        if self.ball.check_paddle_collision(self.player_paddle):
            if self.ball.velocity_x < 0:  # Ball bewegt sich nach links
                self.ball.bounce_off_paddle(self.player_paddle)

        if self.ball.check_paddle_collision(self.bot_paddle):
            if self.ball.velocity_x > 0:  # Ball bewegt sich nach rechts
                self.ball.bounce_off_paddle(self.bot_paddle)

        # Scoring
        if self.ball.x - self.ball.radius < 0:
            # Bot scored (Player verloren)
            self.score_manager.increment_bot_score()
            self.last_scorer = "bot"
            self.ball.x = self.config.SCREEN_WIDTH // 2
            self.ball.y = self.config.SCREEN_HEIGHT // 2
            self.ball.velocity_x = 0
            self.ball.velocity_y = 0
            self.waiting_for_reset = True
            self.reset_timer = pygame.time.get_ticks()

        elif self.ball.x + self.ball.radius > self.config.SCREEN_WIDTH:
            # Player scored (Bot verloren)
            self.score_manager.increment_player_score()
            self.last_scorer = "player"
            self.ball.x = self.config.SCREEN_WIDTH // 2
            self.ball.y = self.config.SCREEN_HEIGHT // 2
            self.ball.velocity_x = 0
            self.ball.velocity_y = 0
            self.waiting_for_reset = True
            self.reset_timer = pygame.time.get_ticks()

        # Gewinner prüfen
        winner = self.score_manager.check_winner()
        if winner:
            self.winner = winner
            self.state = GameState.GAME_OVER

    def render(self) -> None:
        """Rendert den aktuellen Frame."""
        # Hintergrund
        self.screen.fill(self.config.COLOR_BACKGROUND)

        if self.state == GameState.MENU:
            self.menu_buttons = self.ui_renderer.draw_menu()

        elif self.state == GameState.PLAYING:
            # Mittellinie
            self.ui_renderer.draw_center_line()

            # Spielobjekte
            self.player_paddle.draw(self.screen)
            self.bot_paddle.draw(self.screen)
            self.ball.draw(self.screen)

            # Scores
            player_score, bot_score = self.score_manager.get_scores()
            self.ui_renderer.draw_scores(player_score, bot_score)

        elif self.state == GameState.PAUSED:
            # Zeichne Spielfeld im Hintergrund
            self.ui_renderer.draw_center_line()
            self.player_paddle.draw(self.screen)
            self.bot_paddle.draw(self.screen)
            self.ball.draw(self.screen)
            player_score, bot_score = self.score_manager.get_scores()
            self.ui_renderer.draw_scores(player_score, bot_score)

            # Pause Menü darüber
            self.pause_buttons = self.ui_renderer.draw_pause_menu()

        elif self.state == GameState.GAME_OVER:
            self.play_again_button = self.ui_renderer.draw_game_over(self.winner)

        # Display updaten
        pygame.display.flip()

    def run(self) -> None:
        """Hauptspiel-Loop."""
        running = True

        while running:
            # Input verarbeiten
            running = self.handle_input()

            # Spiellogik updaten
            self.update()

            # Rendern
            self.render()

            # FPS begrenzen
            self.clock.tick(self.config.FPS)

        # Cleanup
        pygame.quit()
        sys.exit()
