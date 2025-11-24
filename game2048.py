#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Core 2048 game implementation.
This module provides the basic game mechanics for the 2048 game.
"""

import random
from typing import List, Tuple, Optional


class Game2048:
    """
    A 2048 game implementation.
    
    The board is represented as a 4x4 grid where each cell contains:
    - 0 for empty cells
    - A power of 2 (2, 4, 8, 16, ...) for tiles
    
    Moves are represented as:
    - 0: up
    - 1: down
    - 2: left
    - 3: right
    """
    
    BOARD_SIZE = 4
    
    def __init__(self, board: Optional[List[List[int]]] = None):
        """
        Initialize a new game.
        
        Args:
            board: Optional initial board state (4x4 grid). If None, starts a new game.
        """
        if board is None:
            self.board = [[0] * self.BOARD_SIZE for _ in range(self.BOARD_SIZE)]
            self.score = 0
            self._add_random_tile()
            self._add_random_tile()
        else:
            self.board = [row[:] for row in board]  # Deep copy
            self.score = self._calculate_score()
    
    def _calculate_score(self) -> int:
        """Calculate the score from the current board state."""
        # Score is the sum of all tile values
        return sum(sum(row) for row in self.board)
    
    def get_board(self) -> List[List[int]]:
        """Get a copy of the current board state."""
        return [row[:] for row in self.board]
    
    def get_score(self) -> int:
        """Get the current score."""
        return self.score
    
    def _slide_row_left(self, row: List[int]) -> Tuple[List[int], int]:
        """
        Slide a row to the left and merge identical tiles.
        
        Returns:
            Tuple of (new_row, score_increase)
        """
        # Remove zeros
        new_row = [val for val in row if val != 0]
        score_increase = 0
        
        # Merge identical adjacent tiles
        merged = []
        i = 0
        while i < len(new_row):
            if i < len(new_row) - 1 and new_row[i] == new_row[i + 1]:
                # Merge tiles
                merged_value = new_row[i] * 2
                merged.append(merged_value)
                score_increase += merged_value
                i += 2
            else:
                merged.append(new_row[i])
                i += 1
        
        # Pad with zeros
        merged.extend([0] * (self.BOARD_SIZE - len(merged)))
        return merged[:self.BOARD_SIZE], score_increase
    
    def _slide_row_right(self, row: List[int]) -> Tuple[List[int], int]:
        """Slide a row to the right and merge identical tiles."""
        new_row, score_increase = self._slide_row_left(row[::-1])
        return new_row[::-1], score_increase
    
    def _transpose(self, board: List[List[int]]) -> List[List[int]]:
        """Transpose the board (swap rows and columns)."""
        return [[board[j][i] for j in range(self.BOARD_SIZE)] for i in range(self.BOARD_SIZE)]
    
    def _move_left(self) -> int:
        """Move all tiles left. Returns the score increase."""
        total_score = 0
        for i in range(self.BOARD_SIZE):
            self.board[i], score = self._slide_row_left(self.board[i])
            total_score += score
        return total_score
    
    def _move_right(self) -> int:
        """Move all tiles right. Returns the score increase."""
        total_score = 0
        for i in range(self.BOARD_SIZE):
            self.board[i], score = self._slide_row_right(self.board[i])
            total_score += score
        return total_score
    
    def _move_up(self) -> int:
        """Move all tiles up. Returns the score increase."""
        # Transpose, move left, transpose back
        self.board = self._transpose(self.board)
        score = self._move_left()
        self.board = self._transpose(self.board)
        return score
    
    def _move_down(self) -> int:
        """Move all tiles down. Returns the score increase."""
        # Transpose, move right, transpose back
        self.board = self._transpose(self.board)
        score = self._move_right()
        self.board = self._transpose(self.board)
        return score
    
    def _get_empty_cells(self) -> List[Tuple[int, int]]:
        """Get a list of coordinates of empty cells."""
        empty = []
        for i in range(self.BOARD_SIZE):
            for j in range(self.BOARD_SIZE):
                if self.board[i][j] == 0:
                    empty.append((i, j))
        return empty
    
    def _add_random_tile(self) -> bool:
        """
        Add a random tile (2 or 4) to a random empty cell.
        
        Returns:
            True if a tile was added, False if the board is full.
        """
        empty_cells = self._get_empty_cells()
        if not empty_cells:
            return False
        
        # 90% chance of 2, 10% chance of 4
        value = 2 if random.random() < 0.9 else 4
        row, col = random.choice(empty_cells)
        self.board[row][col] = value
        return True
    
    def execute_move(self, move: int) -> bool:
        """
        Execute a move.
        
        Args:
            move: 0=up, 1=down, 2=left, 3=right
        
        Returns:
            True if the move was valid (board changed), False otherwise.
        """
        # Save current board state
        old_board = [row[:] for row in self.board]
        
        # Execute move
        if move == 0:  # up
            score_increase = self._move_up()
        elif move == 1:  # down
            score_increase = self._move_down()
        elif move == 2:  # left
            score_increase = self._move_left()
        elif move == 3:  # right
            score_increase = self._move_right()
        else:
            return False
        
        # Check if board changed
        if old_board == self.board:
            return False
        
        # Update score
        self.score += score_increase
        
        # Add a random tile
        self._add_random_tile()
        
        return True
    
    def is_move_valid(self, move: int) -> bool:
        """
        Check if a move is valid (would change the board).
        
        Args:
            move: 0=up, 1=down, 2=left, 3=right
        
        Returns:
            True if the move is valid, False otherwise.
        """
        # Create a temporary copy to test the move
        temp_board = [row[:] for row in self.board]
        original_board = self.board
        
        # Temporarily replace board
        self.board = temp_board
        
        # Try the move without adding a random tile
        if move == 0:  # up
            self._move_up()
        elif move == 1:  # down
            self._move_down()
        elif move == 2:  # left
            self._move_left()
        elif move == 3:  # right
            self._move_right()
        else:
            self.board = original_board
            return False
        
        # Check if board changed
        changed = temp_board != original_board
        
        # Restore board
        self.board = original_board
        
        return changed
    
    def has_valid_moves(self) -> bool:
        """Check if there are any valid moves available."""
        for move in range(4):
            if self.is_move_valid(move):
                return True
        return False
    
    def is_game_over(self) -> bool:
        """Check if the game is over (no valid moves)."""
        return not self.has_valid_moves()
    
    def is_won(self) -> bool:
        """Check if the game is won (has a 2048 tile)."""
        for row in self.board:
            if 2048 in row:
                return True
        return False
    
    def get_max_tile(self) -> int:
        """Get the maximum tile value on the board."""
        return max(max(row) for row in self.board)
    
    def __str__(self) -> str:
        """String representation of the board."""
        lines = []
        for row in self.board:
            lines.append(' '.join(f'{val:5d}' if val > 0 else '     .' for val in row))
        return '\n'.join(lines)
    
    def __repr__(self) -> str:
        """Representation of the game state."""
        return f"Game2048(score={self.score}, max_tile={self.get_max_tile()})"


def movename(move: int) -> str:
    """Convert move number to name."""
    names = ['up', 'down', 'left', 'right']
    return names[move] if 0 <= move < len(names) else 'unknown'


if __name__ == '__main__':
    # Simple test/demo
    game = Game2048()
    print("Initial board:")
    print(game)
    print(f"Score: {game.get_score()}")
    print()
    
    # Try a few moves
    for move_name in ['left', 'up', 'right', 'down']:
        move = ['up', 'down', 'left', 'right'].index(move_name)
        if game.execute_move(move):
            print(f"Move: {move_name}")
            print(game)
            print(f"Score: {game.get_score()}")
            print()

