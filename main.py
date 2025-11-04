"""
Main Entry Point
Starts the Pong game application.
"""

from game import PongGame


def main():
    """
    Main function - Entry point of the application.
    Initializes and runs the Pong game.
    Catches and prints any unexpected errors.
    """
    try:
        game = PongGame()
        game.run()
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
