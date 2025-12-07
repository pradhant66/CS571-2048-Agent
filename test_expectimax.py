#!/usr/bin/env python3
"""
Test script to evaluate Expectimax agent performance.
Runs multiple games and collects statistics.
"""

import sys
import time
from game_files import logic
from game_files import constants as c
from agents.expectimax import ExpectimaxAgent
from agents.naive import RandomAgent


def run_single_game(agent, max_moves=10000, verbose=False, silent=False):
    """
    Run a single game with the given agent.
    
    Returns:
        dict with game statistics
    """
    # Initialize game
    matrix = logic.new_game(c.GRID_LEN)
    total_score = 0
    moves = 0
    
    # Create a mock game_grid object with direction_map
    class MockGameGrid:
        def __init__(self, matrix):
            self.matrix = matrix
            self.direction_map = {
                'up': logic.up,
                'down': logic.down,
                'left': logic.left,
                'right': logic.right
            }
    
    game_grid = MockGameGrid(matrix)
    
    # Play until game over or max moves
    while moves < max_moves:
        # Check if game is over
        state = logic.game_state(matrix)
        if state in ['win', 'lose']:
            break
        
        # Get agent's move
        game_grid.matrix = matrix
        direction = agent.next_move(game_grid)
        
        if direction is None:
            break
        
        # Execute move
        move_func = game_grid.direction_map[direction]
        new_matrix, done, score = move_func(matrix)
        
        if not done:
            # Invalid move
            if verbose and not silent:
                print(f"Move {moves}: {direction} was invalid")
            continue
        
        # Update state
        matrix = logic.add_two(new_matrix)
        total_score += score
        moves += 1
        
        if verbose and moves % 50 == 0 and not silent:
            max_tile = max(max(row) for row in matrix)
            print(f"Move {moves}: Score={total_score}, Max tile={max_tile}")
    
    # Get final statistics
    max_tile = max(max(row) for row in matrix)
    final_state = logic.game_state(matrix)
    
    return {
        'score': total_score,
        'max_tile': max_tile,
        'moves': moves,
        'won': final_state == 'win',
        'matrix': matrix
    }


def run_multiple_games(agent_class, num_games=10, verbose=False, silent_progress=False):
    """
    Run multiple games and collect statistics.
    """
    print(f"\n{'='*60}")
    print(f"Testing {agent_class.__name__}")
    print(f"Running {num_games} games...")
    print(f"{'='*60}\n")
    
    results = []
    start_time = time.time()
    
    for i in range(num_games):
        if not silent_progress:
            print(f"Game {i+1}/{num_games}...", end=' ', flush=True)
        
        agent = agent_class()
        result = run_single_game(agent, verbose=verbose, silent=silent_progress)
        results.append(result)
        
        if not silent_progress:
            print(f"Score: {result['score']}, Max tile: {result['max_tile']}, Moves: {result['moves']}")
    
    elapsed_time = time.time() - start_time
    
    # Calculate statistics
    scores = [r['score'] for r in results]
    max_tiles = [r['max_tile'] for r in results]
    moves = [r['moves'] for r in results]
    wins = sum(1 for r in results if r['won'])
    
    # Count tile achievements
    tile_counts = {}
    for tile in [128, 256, 512, 1024, 2048, 4096]:
        count = sum(1 for t in max_tiles if t >= tile)
        tile_counts[tile] = count
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"SUMMARY - {agent_class.__name__}")
    print(f"{'='*60}")
    print(f"Total games: {num_games}")
    print(f"Total time: {elapsed_time:.2f} seconds")
    print(f"Avg time per game: {elapsed_time/num_games:.2f} seconds")
    print(f"\nScore Statistics:")
    print(f"  Average: {sum(scores)/len(scores):.2f}")
    print(f"  Min: {min(scores)}")
    print(f"  Max: {max(scores)}")
    print(f"\nMax Tile Statistics:")
    print(f"  Average: {sum(max_tiles)/len(max_tiles):.2f}")
    print(f"  Min: {min(max_tiles)}")
    print(f"  Max: {max(max_tiles)}")
    print(f"\nMove Statistics:")
    print(f"  Average: {sum(moves)/len(moves):.2f}")
    print(f"  Min: {min(moves)}")
    print(f"  Max: {max(moves)}")
    print(f"\nTile Achievements:")
    for tile, count in sorted(tile_counts.items()):
        percentage = (count / num_games) * 100
        print(f"  {tile:4d}: {count:2d}/{num_games} ({percentage:5.1f}%)")
    print(f"\nWin Rate: {wins}/{num_games} ({(wins/num_games)*100:.1f}%)")
    print(f"{'='*60}\n")
    
    return results


def main():
    """Main entry point for testing."""
    # Parse command line arguments
    num_games = 5  # Default
    verbose = False
    
    if len(sys.argv) > 1:
        try:
            num_games = int(sys.argv[1])
        except ValueError:
            print(f"Invalid number of games: {sys.argv[1]}")
            sys.exit(1)
    
    if len(sys.argv) > 2 and sys.argv[2] == '-v':
        verbose = True
    
    print("\n" + "="*60)
    print("2048 Agent Performance Testing")
    print("="*60)
    
    # Test Expectimax agent
    print("\n" + "="*60)
    print("TESTING EXPECTIMAX AGENT")
    print("="*60)
    # Create agent class that disables verbose output during testing
    ExpectimaxQuiet = lambda: ExpectimaxAgent(verbose=False)
    ExpectimaxQuiet.__name__ = "ExpectimaxAgent"
    expectimax_results = run_multiple_games(ExpectimaxQuiet, num_games, verbose)
    
    # Optional: Test random agent for comparison
    print("\n\n" + "="*60)
    print("TESTING RANDOM AGENT (for comparison)")
    print("="*60)
    random_results = run_multiple_games(RandomAgent, num_games, verbose)
    
    # Compare results
    exp_avg_score = sum(r['score'] for r in expectimax_results) / len(expectimax_results)
    rand_avg_score = sum(r['score'] for r in random_results) / len(random_results)
    improvement = ((exp_avg_score - rand_avg_score) / rand_avg_score) * 100
    
    exp_avg_tile = sum(r['max_tile'] for r in expectimax_results) / len(expectimax_results)
    rand_avg_tile = sum(r['max_tile'] for r in random_results) / len(random_results)
    
    print(f"\n{'='*60}")
    print("FINAL COMPARISON")
    print(f"{'='*60}")
    print(f"\nExpectimax Agent:")
    print(f"  Average score: {exp_avg_score:.2f}")
    print(f"  Average max tile: {exp_avg_tile:.2f}")
    print(f"\nRandom Agent:")
    print(f"  Average score: {rand_avg_score:.2f}")
    print(f"  Average max tile: {rand_avg_tile:.2f}")
    print(f"\nImprovement:")
    print(f"  Score improvement: {improvement:.1f}%")
    print(f"  Tile improvement: {(exp_avg_tile/rand_avg_tile - 1)*100:.1f}%")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()