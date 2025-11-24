# CS571-2048-Agent

This project contains a clean Python implementation of the core 2048 game mechanics, extracted from the [2048-ai](https://github.com/nneonneo/2048-ai) project for building an agentic solver.

## Core Game Implementation

The `game2048.py` module provides the essential game mechanics:

- **Game2048 class**: Main game class with a 4x4 board
- **Move execution**: Up, down, left, right moves with tile merging
- **Score tracking**: Automatic score calculation from merged tiles
- **Game state**: Check for game over, win conditions, and valid moves
- **Random tile placement**: Automatic placement of 2s and 4s after moves

## Usage

```python
from game2048 import Game2048, movename

# Create a new game
game = Game2048()

# Execute moves (0=up, 1=down, 2=left, 3=right)
game.execute_move(2)  # Move left

# Check game state
print(f"Score: {game.get_score()}")
print(f"Max tile: {game.get_max_tile()}")
print(f"Game over: {game.is_game_over()}")
print(f"Won: {game.is_won()}")

# Check if a move is valid
if game.is_move_valid(0):
    game.execute_move(0)  # Move up

# Get board state
board = game.get_board()  # Returns a 4x4 list of lists
```

## Example

Run `python example.py` to see a simple demonstration of the game.

## Browser Control

The project also includes browser control capabilities to interact with 2048 games running in Chrome.

### Setup

1. Install the required dependency:
   ```bash
   pip install websocket-client
   ```

2. Start Chrome with remote debugging enabled:
   ```bash
   chrome --remote-debugging-port=9222 --remote-allow-origins=http://localhost:9222
   ```
   
   On Windows:
   ```bash
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --remote-allow-origins=http://localhost:9222
   ```

3. Open the 2048 game in Chrome (e.g., https://play2048.co/)

### Usage

```python
from chromectrl import ChromeDebuggerControl
from browser_game import Hybrid2048Control

# Connect to Chrome
chrome_ctrl = ChromeDebuggerControl(port=9222)

# Create game controller
game_ctrl = Hybrid2048Control(chrome_ctrl)

# Get game state
board = game_ctrl.get_board()  # Returns log2 values (0=empty, 1=2, 2=4, etc.)
score = game_ctrl.get_score()
status = game_ctrl.get_status()  # 'running', 'won', or 'ended'

# Execute moves (0=up, 1=down, 2=left, 3=right)
game_ctrl.execute_move(2)  # Move left
```

**Note:** The browser control returns board values in log2 representation (0=empty, 1=2, 2=4, 3=8, etc.). Use the conversion functions in `browser_game.py` if you need actual tile values.

Run `python browser_example.py` to see a demonstration.

## Building Your Agent

You can now build your agentic solver on top of this core game implementation. The `Game2048` class provides all the necessary methods to:
- Test different moves
- Evaluate board states
- Simulate game outcomes
- Track scores and game progress

You can also use the browser control to test your agent on real browser games!