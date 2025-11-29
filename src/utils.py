import os
import sys
import numpy as np
import random
import re
from rich.console import Console
console = Console(force_terminal=True, markup=True, color_system="truecolor")

def setup_board(size = 10):
    """Sets up a battleship board of given size."""
    board = np.full((size, size), '_')
    return board

def populate_board(board, ship_lengths):
    """Populates the board with ships of given lengths."""
    for length in ship_lengths:
        board = place_ship(length, board)
    return board

def rect_has_ship(board, r0, c0, r1, c1):
    """Return True if any 'O' is inside the rectangle [r0..r1, c0..c1] (inclusive)."""
    # Clip to board bounds
    n = len(board)
    r0 = max(0, r0)
    r1 = min(n - 1, r1)
    c0 = max(0, c0)
    c1 = min(n - 1, c1)
    
    for row in range(r0, r1 + 1):
        if 'O' in board[row, c0:c1 + 1]:
            return True
    return False


def it_fits(length, origin, orientation, board):
    """Checks if a ship of given length fits on the board from the origin in the specified orientation."""
    n = len(board)
    r = origin[0]
    c = origin[1]
    if orientation == 'H':
        # End cell of the ship
        end_c = c + length - 1
        if end_c >= n:  # off the right edge
            return False
        # Expanded rectangle: one cell of water around the ship
        r0 = r - 1
        c0 = c - 1
        r1 = r + 1
        c1 = end_c + 1
        # Must be empty
        if rect_has_ship(board, r0, c0, r1, c1):
            return False

    else:  # Vertical
        # End cell of the ship
        end_r = r + length - 1
        if end_r >= n:  # off the bottom edge
            return False
        # Expanded rectangle: one cell of water around the ship
        r0 = r - 1
        c0 = c - 1
        r1 = end_r + 1
        c1 = c + 1
        # Must be empty
        if rect_has_ship(board, r0, c0, r1, c1):
            return False 

    return True


def place_ship(length, board):
    """Creates a ship of given length and places it on the board."""
    max_attempts = 10000
    attempts = 1
    while True:
        if attempts > max_attempts:
            print(f"Failed to place ship after {max_attempts} attempts.")
            sys.exit(1)
        # Random origin cell
        origin = (random.randint(0, len(board) - 1), random.randint(0, len(board) - 1))
        orientation = random.choice(['H', 'V'])
        if it_fits(length, origin, orientation, board):
            if orientation == 'H':
                for c in range(length):
                    board[origin[0], origin[1] + c] = 'O'
            else:  # Vertical
                for r in range(length):
                    board[origin[0] + r, origin[1]] = 'O'
            return board
        attempts += 1

def fire(cell, board):
    """Fires at the given cell on the board. Returns True if hit, False if miss."""
    r = cell[0]
    c = cell[1]
    if board[r, c] == 'O':
        board[r, c] = 'X'  # Hit
        return True
    elif board[r, c] == '_':
        board[r, c] = 'A'  # Miss
        return False
    else:
        # Already fired upon
        return None

def scan_board(board):
    """Scans the board and returns the number of ships remaining."""
    #ship_cells = board.tolist().count('O')
    ship_cells = (board == 'O').sum()
    return ship_cells

def random_cell_from_board(board):
    """
    Scans the board and 
    returns a random cell 
    from all available cells.
    """
    empty_cells = []
    for r, row in enumerate(board):
        for c, val in enumerate(row):
            if val == '_':
                empty_cells.append((r, c))
    r, c = random.choice(empty_cells)
    return r, c

def initial_firing_strategy(cell, board):
    """Scans the board and returns a dictionary of 4 lists from all 4 directions from a hit cell, each list containing all available cells in that direction until a non-empty cell."""
    r = cell[0]
    c = cell[1]
    n = len(board)
    strategy = {'dir': '', 'up': [], 'down': [], 'left': [], 'right': []}
    
    # Up
    for i in range(r - 1, -1, -1): # from r-1 to 0
        if board[i, c] == '_':
            strategy['up'].append((i, c))
        else:
            break
    
    # Down
    for i in range(r + 1, n): # from r+1 to n-1
        if board[i, c] == '_':
            strategy['down'].append((i, c))
        else:
            break
    
    # Left
    for j in range(c - 1, -1, -1): # from c-1 to 0
        if board[r, j] == '_':
            strategy['left'].append((r, j))
        else:
            break
    
    # Right
    for j in range(c + 1, n): # from c+1 to n-1
        if board[r, j] == '_':
            strategy['right'].append((r, j))
        else:
            break
    
    return strategy

def update_firing_strategy(shot, cell, strategy):
    if shot == 'X':  # Hit
        if strategy['dir'] == '':
            # Determine direction based on available cells
            if cell in strategy['up']:
                strategy['dir'] = 'V'
                strategy['left'] = []
                strategy['right'] = []
                strategy['up'].remove(cell)
            elif cell in strategy['down']:
                strategy['dir'] = 'V'
                strategy['left'] = []
                strategy['right'] = []
                strategy['down'].remove(cell)
            elif cell in strategy['left']:
                strategy['dir'] = 'H'
                strategy['up'] = []
                strategy['down'] = []
                strategy['left'].remove(cell)
            elif cell in strategy['right']:
                strategy['dir'] = 'H'
                strategy['up'] = []
                strategy['down'] = []
                strategy['right'].remove(cell)
        else:
            # Continue in the same direction
            if strategy['dir'] == 'V':
                if cell in strategy['up']:
                    strategy['up'].remove(cell)
                elif cell in strategy['down']:
                    strategy['down'].remove(cell)
            elif strategy['dir'] == 'H':
                if cell in strategy['left']:
                    strategy['left'].remove(cell)
                elif cell in strategy['right']:
                    strategy['right'].remove(cell)
    elif shot == 'A':  # Miss
        # Clear that direction
        if cell in strategy['up']:
            strategy['up'] = []
        elif cell in strategy['down']:
            strategy['down'] = []
        elif cell in strategy['left']:
            strategy['left'] = []
        elif cell in strategy['right']:
            strategy['right'] = []
    
    # Check if all directions are exhausted
    if not strategy['up'] and not strategy['down'] and not strategy['left'] and not strategy['right']:
        return None  # Strategy exhausted
    return strategy

def next_cell_from_strategy(strategy):
    """Returns the next cell to fire upon based on the current strategy."""
    if strategy['dir'] == 'V':
        if strategy['up']:
            return strategy['up'][0]
        elif strategy['down']:
            return strategy['down'][0]
    elif strategy['dir'] == 'H':
        if strategy['left']:
            return strategy['left'][0]
        elif strategy['right']:
            return strategy['right'][0]
    else:
        # No direction determined yet, pick from the longest available direction
        longest_dir = longest_list_key(strategy)
        if longest_dir:
            return strategy[longest_dir][0]
    # No available cells
    return None

def longest_list_key(strategy):
    longest_key = None
    longest_len = -1

    for k, v in strategy.items():
        if type(v) == list:
            n = len(v)
            if n > longest_len:
                longest_key = k
                longest_len = n

    return longest_key

def parse_cell(cell, size):
    """
    Parse a cell like 'F6' into (row, col).
    Returns (row, col) on success, or None on failure.
    """
    # First check for the 'quit' command
    if cell.strip().lower() == 'quit':
        return 'quit'
    
    # Regex to match a letter followed by 1 or 2 digits
    m = re.fullmatch(r"[\s\.,_-]*([A-Za-z])[\s\.,_-]*(\d{1,2})[\s\.,_-]*", cell)
    if not m:
        return None

    row_letter = m.group(1).upper()
    col_num = int(m.group(2))

    # Check board boundaries
    max_row_letter = chr(ord('A') + size - 1)
    if row_letter < 'A' or row_letter > max_row_letter:
        return None
    if col_num < 1 or col_num > size:
        return None

    row = ord(row_letter) - ord('A')
    col = col_num - 1
    return (row, col)

def clear():
    # Works on Windows (cls) and Unix (clear)
    os.system('cls' if os.name == 'nt' else 'clear')

def display_boards(board_1, board_2):
    """Displays the boards in a readable format."""
    size = len(board_1)
    gap = '     '
    is_two_line_header = False
    h_header = list(range(1, size + 1))
    v_header = [chr(i) for i in range(65, 65 + size)]  # ASCII A, B, C...
    h_header_str = ''
    if size < 10:
        # Single-line header
        h_header_str = ' '.join(map(str, h_header))
    else:
        # Two-line header
        is_two_line_header = True
        units_line = []
        tens_line = []
        for n in h_header:
            if n < 10:
                tens_line.append(' ')
                units_line.append(str(n))
            else:
                n_str = str(n)
                tens_line.append(n_str[0])
                units_line.append(n_str[1])
        
        # Join the digit lists into the header strings
        h_header_tens_str = ' '.join(tens_line)
        h_header_units_str = ' '.join(units_line)
        # The grid width is now based on the units line
        h_header_str = h_header_units_str

    # Panel width includes the row letter ('A ') and the grid numbers
    panel_width = len(h_header_str) + 2

    # Determine the appropriate title version
    if panel_width >= len("Computer's Sea"):
        title1 = "Computer's Sea"
        title2 = "Your Sea"
    elif panel_width >= len("Comp's Sea"):
        title1 = "Comp's Sea"
        title2 = "Your Sea"
    else:
        title1 = "Comp"
        title2 = "You"
        
    # Create the centered title string using f-strings and the .center() method
    titles_line = f"{title1.center(panel_width)}{gap}{title2.center(panel_width)}"
   
    clear()
    console.print(f"[bold white]{titles_line}[/bold white]")
    print()
    if is_two_line_header:
        # Print the tens line first
        print(f"{'  ' + h_header_tens_str}{gap}{'  ' + h_header_tens_str}")
        # Then print the units line
        print(f"{'  ' + h_header_units_str}{gap}{'  ' + h_header_units_str}")
    else:
        # Just one header line
        print(f"{'  ' + h_header_str}{gap}{'  ' + h_header_str}")

    for i in range(size):
        row1 = [f"[{get_style(ch)}]{ch}[/{get_style(ch)}]" for ch in board_1[i, :].tolist()]
        row2 = [f"[{get_style(ch)}]{ch}[/{get_style(ch)}]" for ch in board_2[i, :].tolist()]
        console.print(
            f"{v_header[i]} " + " ".join(row1)
            + gap +
            f"{v_header[i]} " + " ".join(row2)
        )

    # for i in range(size):
    #     rich.print(v_header[i] + ' ' + ' '.join(board_1[i, :]) + gap + \
    #           v_header[i] + ' ' + ' '.join(board_2[i, :]))
    print()

def get_style(char):
    """Returns the rich style for a given board character."""
    ch = str(char).strip()
    if ch == "_":
        return "dim #2f2f2f"
    if ch == "X":
        return "bold #ff1744"
    if ch == "O":
        return "bold #e6e6e6"
    if ch == "A":
        return "#64b5f6"
    return ""




if __name__ == "__main__":
    print()


