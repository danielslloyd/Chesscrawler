#!/usr/bin/env python3
"""
Chess Dungeon Crawler - Main Entry Point

A unique dungeon crawler where characters move using chess piece mechanics!
"""

from game import Game


def main():
    """Main entry point."""
    print("=" * 60)
    print("        CHESS DUNGEON CRAWLER")
    print("=" * 60)
    print()
    print("Welcome, adventurer!")
    print()
    print("In this dungeon crawler, your party moves using chess rules.")
    print("Each character combines an RPG class with chess movement.")
    print()
    print("Key Features:")
    print("  - Click characters to select and move them")
    print("  - Characters can 'capture' allies to swap movement types")
    print("  - Blue highlights = valid moves")
    print("  - Red highlights = attackable enemies")
    print("  - Defeat all enemies and the boss to win!")
    print()
    print("Controls:")
    print("  Mouse Click: Select/Move/Attack")
    print("  Tab: Cycle through party members")
    print("  Space: End turn")
    print("  1-6: Quick select party members")
    print("  ESC: Quit")
    print()
    print("=" * 60)
    print()

    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"\nError running game: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
