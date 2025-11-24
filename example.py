#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example usage of the Game2048 class.
"""

from game2048 import Game2048, movename


def main():
    """Run a simple example game."""
    game = Game2048()
    
    print("Starting a new 2048 game!")
    print("=" * 40)
    print(game)
    print(f"Score: {game.get_score()}")
    print()
    
    # Play until game over
    move_count = 0
    while not game.is_game_over():
        # Find a valid move
        valid_moves = [move for move in range(4) if game.is_move_valid(move)]
        
        if not valid_moves:
            break
        
        # Use the first valid move (you can replace this with your agent's logic)
        move = valid_moves[0]
        move_count += 1
        
        print(f"Move #{move_count}: {movename(move)}")
        game.execute_move(move)
        print(game)
        print(f"Score: {game.get_score()}, Max tile: {game.get_max_tile()}")
        print()
        
        # Stop after a reasonable number of moves for demo
        if move_count >= 20:
            print("Stopping after 20 moves for demo purposes.")
            break
    
    print("=" * 40)
    print("Game Over!")
    print(f"Final Score: {game.get_score()}")
    print(f"Max Tile: {game.get_max_tile()}")
    print(f"Total Moves: {move_count}")


if __name__ == '__main__':
    main()

