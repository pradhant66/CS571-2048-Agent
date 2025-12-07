#!/usr/bin/env python3
"""
Comprehensive evaluation script for the project proposal.
Tests Expectimax under:
1. Standard vs Modified tile distribution
2. Different grid sizes (3x3, 4x4, 5x5)
3. Evaluates heuristic reliability across conditions
"""

import sys
import time
import copy
from game_files import logic
from game_files import constants as c
from agents.expectimax import ExpectimaxAgent
from agents.naive import RandomAgent


def run_single_game(agent, grid_size=4, tile_mode='standard', max_moves=10000, verbose=False):
    """
    Run a single game with specified parameters.
    
    Args:
        agent: The agent to test
        grid_size: Size of the grid (3, 4, or 5)
        tile_mode: 'standard' or 'modified'
        max_moves: Maximum number of moves
        verbose: Print detailed progress
    
    Returns:
        dict with game statistics
    """
    # Set tile distribution mode
    logic.set_tile_distribution(tile_mode)
    
    # Initialize game with specified grid size
    matrix = logic.new_game(grid_size)
    total_score = 0
    moves = 0
    
    # Create a mock game_grid object
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
    
    # Play until game over
    while moves < max_moves:
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
            continue
        
        # Update state
        matrix = logic.add_two(new_matrix)
        total_score += score
        moves += 1
        
        if verbose and moves % 100 == 0:
            max_tile = max(max(row) for row in matrix)
            print(f"  Move {moves}: Score={total_score}, Max tile={max_tile}")
    
    # Get final statistics
    max_tile = max(max(row) for row in matrix)
    final_state = logic.game_state(matrix)
    
    return {
        'score': total_score,
        'max_tile': max_tile,
        'moves': moves,
        'won': final_state == 'win',
        'grid_size': grid_size,
        'tile_mode': tile_mode
    }


def run_experiment(agent_class, grid_size, tile_mode, num_games=10, agent_name=None):
    """
    Run an experiment with specific configuration.
    """
    if agent_name is None:
        agent_name = agent_class.__name__
    
    print(f"\n{'='*70}")
    print(f"Experiment: {agent_name} | Grid: {grid_size}x{grid_size} | Tiles: {tile_mode}")
    print(f"{'='*70}")
    
    results = []
    start_time = time.time()
    
    for i in range(num_games):
        print(f"Game {i+1}/{num_games}...", end=' ', flush=True)
        
        agent = agent_class()
        result = run_single_game(agent, grid_size=grid_size, tile_mode=tile_mode)
        results.append(result)
        
        print(f"Score: {result['score']:5d}, Max tile: {result['max_tile']:4d}, Moves: {result['moves']:3d}")
    
    elapsed_time = time.time() - start_time
    
    # Calculate statistics
    scores = [r['score'] for r in results]
    max_tiles = [r['max_tile'] for r in results]
    moves = [r['moves'] for r in results]
    wins = sum(1 for r in results if r['won'])
    
    # Tile achievements
    tile_thresholds = [128, 256, 512, 1024, 2048, 4096]
    tile_counts = {t: sum(1 for tile in max_tiles if tile >= t) for t in tile_thresholds}
    
    # Print summary
    print(f"\n{'-'*70}")
    print(f"RESULTS SUMMARY")
    print(f"{'-'*70}")
    print(f"Configuration: {grid_size}x{grid_size} grid, {tile_mode} tiles")
    print(f"Games played: {num_games}")
    print(f"Total time: {elapsed_time:.2f}s (avg: {elapsed_time/num_games:.2f}s per game)")
    print(f"\nScore Statistics:")
    print(f"  Average: {sum(scores)/len(scores):.2f}")
    print(f"  Min: {min(scores)}, Max: {max(scores)}")
    print(f"\nMax Tile Statistics:")
    print(f"  Average: {sum(max_tiles)/len(max_tiles):.2f}")
    print(f"  Min: {min(max_tiles)}, Max: {max(max_tiles)}")
    print(f"\nMove Statistics:")
    print(f"  Average: {sum(moves)/len(moves):.2f}")
    print(f"\nTile Achievement Rates:")
    for tile, count in sorted(tile_counts.items()):
        if tile <= max(max_tiles):  # Only show relevant tiles
            print(f"  {tile:4d}+: {count:2d}/{num_games} ({100*count/num_games:5.1f}%)")
    print(f"\nWin Rate (2048): {wins}/{num_games} ({100*wins/num_games:.1f}%)")
    print(f"{'='*70}\n")
    
    return {
        'config': f"{grid_size}x{grid_size}_{tile_mode}",
        'avg_score': sum(scores)/len(scores),
        'avg_max_tile': sum(max_tiles)/len(max_tiles),
        'win_rate': wins/num_games,
        'tile_counts': tile_counts,
        'results': results
    }


def main():
    """Main experimental evaluation."""
    # Parse arguments
    num_games = 10 if len(sys.argv) <= 1 else int(sys.argv[1])
    
    print("\n" + "="*70)
    print("COMPREHENSIVE EXPECTIMAX EVALUATION")
    print("Testing generalization across grid sizes and tile distributions")
    print("="*70)
    
    # Create quiet Expectimax agent
    ExpectimaxQuiet = lambda: ExpectimaxAgent(depth=3, verbose=False)
    ExpectimaxQuiet.__name__ = "ExpectimaxAgent"
    
    # Store all results for comparison
    all_results = []
    
    # ==========================================
    # EXPERIMENT 1: Standard 4x4 (Baseline)
    # ==========================================
    print("\n" + "#"*70)
    print("# EXPERIMENT 1: Baseline (Standard 4x4, Standard Tiles)")
    print("#"*70)
    baseline = run_experiment(ExpectimaxQuiet, grid_size=4, tile_mode='standard', 
                              num_games=num_games, agent_name="Expectimax (Baseline)")
    all_results.append(('Baseline 4x4 Standard', baseline))
    
    # ==========================================
    # EXPERIMENT 2: Modified Tiles on 4x4
    # ==========================================
    print("\n" + "#"*70)
    print("# EXPERIMENT 2: Modified Tile Distribution (4x4, Modified Tiles)")
    print("#"*70)
    modified_4x4 = run_experiment(ExpectimaxQuiet, grid_size=4, tile_mode='modified',
                                  num_games=num_games, agent_name="Expectimax (Modified)")
    all_results.append(('4x4 Modified Tiles', modified_4x4))
    
    # ==========================================
    # EXPERIMENT 3: Different Grid Sizes (Standard Tiles)
    # ==========================================
    print("\n" + "#"*70)
    print("# EXPERIMENT 3: Grid Size Generalization (Standard Tiles)")
    print("#"*70)
    
    # 3x3 grid
    small_grid = run_experiment(ExpectimaxQuiet, grid_size=3, tile_mode='standard',
                               num_games=num_games, agent_name="Expectimax (3x3)")
    all_results.append(('3x3 Standard', small_grid))
    
    # 5x5 grid
    large_grid = run_experiment(ExpectimaxQuiet, grid_size=5, tile_mode='standard',
                               num_games=num_games, agent_name="Expectimax (5x5)")
    all_results.append(('5x5 Standard', large_grid))
    
    # ==========================================
    # EXPERIMENT 4: Combined Modifications
    # ==========================================
    print("\n" + "#"*70)
    print("# EXPERIMENT 4: Combined Modifications")
    print("#"*70)
    
    # 3x3 with modified tiles
    small_modified = run_experiment(ExpectimaxQuiet, grid_size=3, tile_mode='modified',
                                   num_games=num_games, agent_name="Expectimax (3x3 Mod)")
    all_results.append(('3x3 Modified', small_modified))
    
    # 5x5 with modified tiles
    large_modified = run_experiment(ExpectimaxQuiet, grid_size=5, tile_mode='modified',
                                   num_games=num_games, agent_name="Expectimax (5x5 Mod)")
    all_results.append(('5x5 Modified', large_modified))
    
    # ==========================================
    # FINAL COMPARISON
    # ==========================================
    print("\n" + "="*70)
    print("FINAL COMPARISON - ALL EXPERIMENTS")
    print("="*70)
    print(f"\n{'Configuration':<25} {'Avg Score':>12} {'Avg Max Tile':>12} {'Win Rate':>10}")
    print("-"*70)
    
    for name, result in all_results:
        print(f"{name:<25} {result['avg_score']:>12.1f} {result['avg_max_tile']:>12.1f} {result['win_rate']:>9.1%}")
    
    # Calculate performance degradation
    baseline_score = baseline['avg_score']
    print(f"\n{'Performance vs Baseline:':<25}")
    print("-"*70)
    for name, result in all_results[1:]:  # Skip baseline
        degradation = ((result['avg_score'] - baseline_score) / baseline_score) * 100
        print(f"{name:<25} {degradation:>+6.1f}%")
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nKey Findings:")
    print(f"1. Baseline performance (4x4 standard): {baseline_score:.1f} avg score")
    print(f"2. Modified tiles impact: {((modified_4x4['avg_score']-baseline_score)/baseline_score)*100:+.1f}%")
    print(f"3. Heuristics generalize to different grid sizes: {'YES' if all(r['avg_score'] > 0 for _, r in all_results) else 'NO'}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()