import utils
import random
from time import sleep
import argparse

parser = argparse.ArgumentParser(prog="battleship")
sub = parser.add_subparsers(dest="cmd", required=True)

# Play mode
p_play = sub.add_parser("play", help="Play a game")
p_play.add_argument("--board", type=int, default=10)
p_play.add_argument("--ships", type=int, nargs="+", default=[4,3,3,2,2,2],
                    help="List of ship lengths")

# Demo mode
p_demo = sub.add_parser("demo", help="The computer will play against itself")
p_demo.add_argument("--board", type=int, default=10)
p_demo.add_argument("--ships", type=int, nargs="+", default=[4,3,3,2,2,2],
                    help="List of ship lengths")

args = parser.parse_args()

if args.cmd == "play":
    print("Playing with size:", args.board, "ships:", args.ships)
elif args.cmd == "demo":
    print("Demo with board size:", args.board, "ships:", args.ships)



def main():
    # Set up boards
    size = args.board
    ships = args.ships
    board_user = utils.populate_board(utils.setup_board(size), ships)
    board_comp = utils.populate_board(utils.setup_board(size), ships)
    board_comp_for_user = utils.setup_board(size)
    board_user_for_comp = utils.setup_board(size)
    user_strategy = None
    comp_strategy = None
    max_row_letter = chr(ord('A') + size - 1)
    max_col_num = size

    # Display initial boards
    utils.display_boards(board_comp_for_user, board_user)

    # Game loop
    while True:
        # User's turn
        print("Your turn to fire!")
        while True:
            row = 0
            col = 0
            if args.cmd == "demo":
                sleep(0.5)
                # row = random.randint(0, size - 1)
                # col = random.randint(0, size - 1)
                # row, col = utils.random_cell_from_board(board_comp_for_user)
                if user_strategy == None:
                    row, col = utils.random_cell_from_board(board_comp_for_user)
                else:
                    row, col = utils.next_cell_from_strategy(user_strategy)
            else:
                cell = input(f"Enter cell (A1-{max_row_letter}{max_col_num}): ")
                parsed = utils.parse_cell(cell, size)
                if parsed is None:
                    print(f"Invalid cell. Use a letter A-{max_row_letter} and a number 1-{max_col_num}, e.g., F6")
                    continue
                elif parsed == 'quit':
                    print("Quitting the game. Goodbye!")
                    return
                row, col = parsed
            result = utils.fire((row, col), board_comp)
            if result is None:
                print("Cell already fired upon. Try again.")
                continue
            elif result:
                print("Hit!")
                board_comp_for_user[row, col] = 'X'
                if args.cmd == "demo":
                    if user_strategy == None:
                        user_strategy = utils.initial_firing_strategy((row, col), board_comp_for_user)
                    else:
                        user_strategy = utils.update_firing_strategy('X', (row, col), user_strategy)
            else:
                print("Miss!")
                board_comp_for_user[row, col] = 'A'
                if args.cmd == "demo":
                    if user_strategy != None:
                        user_strategy = utils.update_firing_strategy('A', (row, col), user_strategy)
            utils.display_boards(board_comp_for_user, board_user)
            if utils.scan_board(board_comp) == 0:
                print("Congratulations! You sank all the computer's ships!")
                return
            break

        # Computer's turn
        while True:
            sleep(0.5)
            message = ''
            # row = random.randint(0, size - 1)
            # col = random.randint(0, size - 1)
            if comp_strategy == None:
                row, col = utils.random_cell_from_board(board_user_for_comp)
            else:
                row, col = utils.next_cell_from_strategy(comp_strategy)
            result = utils.fire((row, col), board_user)
            if result is None:
                print("Cell already fired upon. Try again.")
                sleep(0.25)
                continue
            elif result:
                message = f"Computer hit at {chr(row + 65)}{col + 1}!"
                board_user_for_comp[row, col] = 'X'
                if comp_strategy == None:
                    comp_strategy = utils.initial_firing_strategy((row, col), board_user_for_comp)
                else:
                    comp_strategy = utils.update_firing_strategy('X', (row, col), comp_strategy)
            else:
                message = f"Computer missed at {chr(row + 65)}{col + 1}."
                board_user_for_comp[row, col] = 'A'
                if comp_strategy != None:
                    comp_strategy = utils.update_firing_strategy('A', (row, col), comp_strategy)
            utils.display_boards(board_comp_for_user, board_user)
            print(message)
            if utils.scan_board(board_user) == 0:
                print("Sorry, the computer sank all your ships. Game over.")
                return
            break



if __name__ == "__main__":
    main()

