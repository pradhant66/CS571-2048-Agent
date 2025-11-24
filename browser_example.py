#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example of using the browser control to play 2048 in Chrome.

To use this:
1. Start Chrome with remote debugging enabled:
   chrome --remote-debugging-port=9222 --remote-allow-origins=http://localhost:9222
   
   Or on Windows:
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --remote-allow-origins=http://localhost:9222

2. Open the 2048 game in Chrome (e.g., https://play2048.co/)

3. Run this script: python browser_example.py
"""

import time
from chromectrl import ChromeDebuggerControl
from browser_game import Hybrid2048Control, convert_board_log2_to_values
from game2048 import movename


def print_board(board_log2):
    """Print board in a readable format."""
    board = convert_board_log2_to_values(board_log2)
    for row in board:
        print(' '.join(f'{val:5d}' if val > 0 else '     .' for val in row))


def main():
    """Run a simple example controlling the browser game."""
    print("Connecting to Chrome...")
    try:
        chrome_ctrl = ChromeDebuggerControl(port=9222)
        print("Connected!")
    except Exception as e:
        print(f"Error connecting to Chrome: {e}")
        print("\nMake sure Chrome is running with:")
        print("  --remote-debugging-port=9222 --remote-allow-origins=http://localhost:9222")
        return
    
    print("\nSetting up game control...")
    game_ctrl = Hybrid2048Control(chrome_ctrl)
    
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


if __name__ == '__main__':
    main()

