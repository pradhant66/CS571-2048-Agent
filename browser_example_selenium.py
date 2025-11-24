#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example of using Selenium to automatically launch a browser and play 2048.

This version uses Selenium to automatically create and control a browser,
so you don't need to manually start Chrome with remote debugging.

To use:
1. Install selenium: pip install selenium
2. (Optional) Install webdriver-manager for automatic driver management:
   pip install webdriver-manager
3. Run this script: python browser_example_selenium.py
"""

import time
from seleniumctrl import SeleniumControl
from browser_game import Hybrid2048Control, convert_board_log2_to_values
from game2048 import movename


def print_board(board_log2):
    """Print board in a readable format."""
    board = convert_board_log2_to_values(board_log2)
    for row in board:
        print(' '.join(f'{val:5d}' if val > 0 else '     .' for val in row))


def main():
    """Run a simple example controlling the browser game with Selenium."""
    print("Launching browser with Selenium...")
    
    # Use context manager to ensure browser closes properly
    with SeleniumControl(url="https://play2048.co/", headless=False) as selenium_ctrl:
        print("\nSetting up game control...")
        game_ctrl = Hybrid2048Control(selenium_ctrl)
        
        print("Current board:")
        board = game_ctrl.get_board()
        print_board(board)
        print(f"Score: {game_ctrl.get_score()}")
        print()
        
        # Play a few moves
        for i in range(5):
            # Simple strategy: just try moves in order
            for move in range(4):
                status = game_ctrl.get_status()
                if status == 'ended':
                    print("Game over!")
                    return
                elif status == 'won':
                    print("Game won! Continuing...")
                    game_ctrl.continue_game()
                
                # Try the move
                game_ctrl.execute_move(move)
                time.sleep(0.1)  # Small delay to let the game update
                
                # Check if board changed
                new_board = game_ctrl.get_board()
                if new_board != board:
                    print(f"Move {i+1}: {movename(move)}")
                    print_board(new_board)
                    print(f"Score: {game_ctrl.get_score()}")
                    print()
                    board = new_board
                    break
        
        print("Demo complete!")
        print("Browser will close automatically...")
        time.sleep(2)  # Give user a moment to see the final state


if __name__ == '__main__':
    main()

