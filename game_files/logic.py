#
# Modified CS1010FC logic.py
# Supports variable tile distribution modes
#

import random

# Handle imports for both direct execution and package import
try:
    from . import constants as c
except ImportError:
    # When running directly, use relative imports
    import constants as c

# Global variable to control tile distribution mode
TILE_DISTRIBUTION_MODE = 'standard'  # 'standard' or 'modified'

def set_tile_distribution(mode='standard'):
    """
    Set the tile distribution mode.
    
    Args:
        mode: 'standard' for {2, 4} or 'modified' for {2, 4, 8, ..., max_tile}
    """
    global TILE_DISTRIBUTION_MODE
    TILE_DISTRIBUTION_MODE = mode

def new_game(n):
    matrix = []
    for i in range(n):
        matrix.append([0] * n)
    matrix = add_two(matrix)
    matrix = add_two(matrix)
    return matrix

def add_two(mat):
    """Add a new tile to the board based on current distribution mode."""
    a = random.randint(0, len(mat)-1)
    b = random.randint(0, len(mat)-1)
    while mat[a][b] != 0:
        a = random.randint(0, len(mat)-1)
        b = random.randint(0, len(mat)-1)
    
    # Determine tile value based on mode
    if TILE_DISTRIBUTION_MODE == 'standard':
        # Standard 2048: 90% chance of 2, 10% chance of 4
        mat[a][b] = 2 if random.random() < 0.9 else 4
    else:
        # Modified: equal probability for {2, 4, 8, ..., max_tile}
        max_tile = max(max(row) for row in mat)
        if max_tile < 2:
            max_tile = 2
        
        # Generate all powers of 2 up to max_tile
        possible_tiles = []
        power = 1
        while 2**power <= max_tile:
            possible_tiles.append(2**power)
            power += 1
        
        # Choose randomly with equal probability
        mat[a][b] = random.choice(possible_tiles)
    
    return mat

def game_state(mat):
    # check for win cell
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            if mat[i][j] == 2048:
                return 'win'
    # check for any zero entries
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            if mat[i][j] == 0:
                return 'not over'
    # check for same cells that touch each other
    for i in range(len(mat)-1):
        for j in range(len(mat[0])-1):
            if mat[i][j] == mat[i+1][j] or mat[i][j+1] == mat[i][j]:
                return 'not over'
    for k in range(len(mat)-1):  # to check the left/right entries on the last row
        if mat[len(mat)-1][k] == mat[len(mat)-1][k+1]:
            return 'not over'
    for j in range(len(mat)-1):  # check up/down entries on last column
        if mat[j][len(mat)-1] == mat[j+1][len(mat)-1]:
            return 'not over'
    return 'lose'

def reverse(mat):
    new = []
    for i in range(len(mat)):
        new.append([])
        for j in range(len(mat[0])):
            new[i].append(mat[i][len(mat[0])-j-1])
    return new

def transpose(mat):
    new = []
    for i in range(len(mat[0])):
        new.append([])
        for j in range(len(mat)):
            new[i].append(mat[j][i])
    return new

def cover_up(mat):
    new = []
    grid_len = len(mat)
    for j in range(grid_len):
        partial_new = []
        for i in range(grid_len):
            partial_new.append(0)
        new.append(partial_new)
    done = False
    for i in range(grid_len):
        count = 0
        for j in range(grid_len):
            if mat[i][j] != 0:
                new[i][count] = mat[i][j]
                if j != count:
                    done = True
                count += 1
    return new, done

def merge(mat, done):
    score = 0
    grid_len = len(mat)
    for i in range(grid_len):
        for j in range(grid_len-1):
            if mat[i][j] == mat[i][j+1] and mat[i][j] != 0:
                mat[i][j] *= 2
                mat[i][j+1] = 0
                score += mat[i][j]
                done = True
    return mat, done, score

def up(game):
    # print("up")
    game = transpose(game)
    game, done = cover_up(game)
    game, done, score = merge(game, done)
    game = cover_up(game)[0]
    game = transpose(game)
    return game, done, score

def down(game):
    # print("down")
    game = reverse(transpose(game))
    game, done = cover_up(game)
    game, done, score = merge(game, done)
    game = cover_up(game)[0]
    game = transpose(reverse(game))
    return game, done, score

def left(game):
    # print("left")
    game, done = cover_up(game)
    game, done, score = merge(game, done)
    game = cover_up(game)[0]
    return game, done, score

def right(game):
    # print("right")
    game = reverse(game)
    game, done = cover_up(game)
    game, done, score = merge(game, done)
    game = cover_up(game)[0]
    game = reverse(game)
    return game, done, score