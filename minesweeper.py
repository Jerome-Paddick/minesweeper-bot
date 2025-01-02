import time

from collections import defaultdict
from dataclasses import dataclass
from pprint import pprint
from PIL import Image
import numpy as np
import tensorflow as tf
from mouse import click, right_click, move

from display import display_grid
from stop import handle_stop
from utils import print_grid, delete_png_files, red_square, PauseManager
from window import get_window_by_title, capture_window, focus_window


class Board:
    level_map = {
        165: 1,
        117: 2,
        69: 3,
        45: 4,
        0: 5,
    }
    cell_size = 48
    pad_map = {
        1: (17, 124),
        2: (17, 124),
        3: (17, 124),
        4: (17, 124),
        5: (17, 122),
    }
    size_map = {
        1: (9, 9),
        2: (12, 11),
        3: (15, 13),
        4: (18, 14),
        5: (20, 16),
    }
    edge_map = {
        1: (500, 165),
        2: (427, 117),
        3: (356, 69),
        4: (283, 45),
        5: (235, 0)
    }

    def __init__(self, screenshot, known=None, last_level=None, debug=False):
        self.debug = debug
        self.last_level = last_level
        self.known = known

        base_crop = (547, 258, 2014, 1239)

        self.game_window_screenshot = screenshot.crop(base_crop)
        self.game_window_screenshot.save('_base' + '.png')

        self.load_model()

        top = self.find_game_board(screenshot)
        self.level = self.level_map[top]
        self.size = self.size_map[self.level]
        self.edge = self.edge_map[self.level]
        self.pad = self.pad_map[self.level]

        if not known or last_level != level:
            self.known = {}

        self.board_capture = self.game_window_screenshot.crop(self.dimensions())
        self.board_capture.save('_capture.png')

        delete_png_files()

    def find_game_board(self, screenshot):
        top = None
        left = None
        top_laser_x = 750
        left_laser_y = 300

        for y in range(0, 170):
            r, g, b = self.game_window_screenshot.getpixel((top_laser_x, y))
            if r < 60 and g < 80 and b < 90:
                top = y
                break
        else:
            raise ValueError("top laser did not connect")

        for x in range(100, 510):
            r, g, b = self.game_window_screenshot.getpixel((x, left_laser_y))
            if r < 60 and g < 80 and b < 90:
                left = x
                break
        else:
            raise ValueError("left laser did not connect")

        print("top:", top)
        print("left:", left)

        visualise_lasers = self.game_window_screenshot.crop((0, 0, 800, 500))
        red_square(visualise_lasers, (top_laser_x, top))
        red_square(visualise_lasers, (left, left_laser_y))
        visualise_lasers.save('_lasers' + '.png')

        return top

    def real_edge(self):
        x, y = self.edge
        xp, yp = self.pad
        return x + xp, y + yp

    def dimensions(self):
        asdf = 0
        x, y = self.real_edge()
        x_cells, y_cells = self.size_map[self.level]
        x_edge_length, y_edge_length = (x_cells*self.cell_size), (y_cells*self.cell_size)
        return x, y, x + x_edge_length + asdf, y + y_edge_length + asdf

    def load_model(self):
        # Load model and class names
        self.model = tf.keras.models.load_model('simple_classifier.h5')
        with open('class_names.txt', 'r') as f:
            self.class_names = f.read().splitlines()

    def get_cell_grid(self):
        """
        Split the board capture into individual cells and analyze using a trained classifier
        Returns a 2D list of cell states
        """
        if self.known:
            print("known", len(self.known))

        state_map = {
            "0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
            "bg_green": None, "C": "C", "M": "M", "X": "X",
        }

        add_to_known = [0, 1, 2, 3, 4, 5, 6, "X"]

        board_array = np.array(self.board_capture)
        cols, rows = self.size

        grid = []
        for row in range(rows):
            cell_row = []
            for col in range(cols):
                if (
                        self.last_level == self.level and
                        (state:= self.known.get((row, col), None))
                ):
                    cell_row.append(state)
                    continue

                left = col * self.cell_size
                top = row * self.cell_size
                right = left + self.cell_size
                bottom = top + self.cell_size

                cell_color = board_array[top:bottom, left:right]

                if self.debug:
                    cell_img = Image.fromarray(cell_color)
                    cell_img.save(f"img/cell_{row}_{col}_original.png")

                # Resize using numpy
                cell_resized = np.array(Image.fromarray(cell_color).resize((64, 64)))
                cell_normalized = cell_resized / 255.0
                cell_batch = np.expand_dims(cell_normalized, axis=0)

                predictions = self.model.predict(cell_batch, verbose=0)
                predicted_class_idx = np.argmax(predictions[0])
                predicted_class = self.class_names[predicted_class_idx]

                state = state_map[predicted_class]
                cell_row.append(state)

                if state in add_to_known:
                    self.known[(row, col)] = state

            grid.append(cell_row)

        self.last_level = self.level
        # pprint(grid)
        return grid


    def click_cells(self, cell_positions, left_click=True):
        """
        Click multiple cells based on their grid positions.

        Args:
            cell_positions: List of tuples (x, y) representing grid coordinates to click

        Example:
            board.click_cells([(0, 1), (2, 3)])  # Clicks cell at (0,1) and (2,3)
            :param left_click:
        """
        for y, x in cell_positions:
            # Validate coordinates are within bounds
            if not (0 <= x < self.size[0] and 0 <= y < self.size[1]):
                raise ValueError(f"Cell position ({x}, {y}) is out of bounds")

            # Calculate pixel position relative to game window
            edge_x, edge_y = self.real_edge()
            click_x = edge_x + (x * self.cell_size) + (self.cell_size // 2)
            click_y = edge_y + (y * self.cell_size) + (self.cell_size // 2)

            # Since base_crop was applied to screenshot, need to add those offsets back
            base_x, base_y = 547, 258  # From base_crop in __init__
            absolute_x = base_x + click_x
            absolute_y = base_y + click_y

            # Perform the click (you'll need to implement the actual click mechanism)
            # This could be pyautogui.click() or similar
            move(absolute_x, absolute_y)
            time.sleep(0.2)
            if left_click:
                click()
            else:
                right_click()
        move(0, 0)


@dataclass
class Moves:
    special_moves: set[tuple]
    moves: set[tuple]
    moves_mines: set[tuple]

def find_moves(grid):

    rows = len(grid)
    cols = len(grid[0])

    all_none = True
    for row in range(rows):
        for col in range(cols):
            if grid[row][col] is not None:
                all_none = False
                break
        if not all_none:
            break

    # If all cells are None, return all possible positions
    if all_none:
        return Moves(moves={(5, 5)}, special_moves=set(), moves_mines=set())


    unsolved = set()
    frontier = defaultdict(list)
    cardinal = [
        (-1, -1),
        (0, -1),
        (1, -1),
        (-1, 0),
        (1, 0),
        (-1, 1),
        (0, 1),
        (1, 1)
    ]
    unsolved_cells = [None, "C", "M"]
    unsolved_special = ["C", "M"]
    numbers = [1, 2, 3, 4, 5, 6, 7]

    special_moves = set()
    moves = set()
    moves_mines = set()

    for row in range(rows):
        for col in range(cols):
            if grid[row][col] in unsolved_cells:
                unsolved.add((row, col))

    for cell in unsolved:
        x, y = cell
        for dx, dy in cardinal:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < rows and 0 <= new_y < cols:
                if grid[new_x][new_y] in numbers:
                    frontier[cell].append((new_x, new_y))

    if DEBUG:
        display_grid(grid, frontier, "red")

    potential_special_frontier_cells = defaultdict(set)
    potential_mines_frontier_cells = defaultdict(set)
    potential_moves_frontier_cells = defaultdict(set)

    for unsolved, adj in frontier.items():
        for cell in adj:
            x, y = cell
            number = grid[x][y]
            unsolved = []
            flag_count = 0
            special = False


            for dx, dy in cardinal:
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < rows and 0 <= new_y < cols:
                    if grid[new_x][new_y] in unsolved_special:
                        unsolved.append((new_x, new_y))
                        special = True
                    if grid[new_x][new_y] is None:
                        unsolved.append((new_x, new_y))
                    elif grid[new_x][new_y] == "X":
                        flag_count += 1


            unsolved_count = len(unsolved)
            # print("xy", x, y, "-", number)
            # print("unsolved_count", unsolved_count)
            # print("flag_count", flag_count)

            # find real cells
            if flag_count == number and unsolved_count > 0:
                if special:
                    # special_moves.add(cell)
                    for u in unsolved:
                        potential_special_frontier_cells[u].add(cell)
                else:
                    for u in unsolved:
                        potential_moves_frontier_cells[u].add(cell)
                    # moves.add(cell)

            # find mines
            if unsolved_count and unsolved_count + flag_count == number:
                # moves_mines.add((x, y))
                for u in unsolved:
                    potential_mines_frontier_cells[u].add(cell)


    print("potential -->")
    print("spec", potential_special_frontier_cells)
    print("moves", potential_moves_frontier_cells)
    print("mines", potential_mines_frontier_cells)
    print("<---")
    print("special_moves")
    print(special_moves)
    print("moves")
    print(moves)
    print("moves_mines")
    print(moves_mines)

    for k, v in potential_special_frontier_cells.items():
        special_moves.add(v.pop())

    for k, v in potential_mines_frontier_cells.items():
        moves_mines.add(v.pop())

    for k, v in potential_moves_frontier_cells.items():
        moves.add(v.pop())

    return Moves(special_moves, moves, moves_mines)


def make_moves(grid, moves):
    ...

if __name__ == '__main__':
    handle_stop()

    DEBUG = False

    window_title = "Dota 2"
    window = get_window_by_title(window_title)
    focus_window(window)

    with PauseManager():
        screenshot = capture_window(window)

    level = None
    known = None

    while True:
        start = time.time()

        board = Board(
            screenshot=screenshot,
            known=known,
            last_level=level,
        )
        grid = board.get_cell_grid()

        moves = find_moves(grid)
        print_grid(grid)

        if not (moves.special_moves or moves.moves or moves.moves_mines):
            print("\n" + "*" * 50 + "\n\tMOVE NOT FOUND\n" + "*" * 50 + "\n")
            input("Press Enter to run when moves available...")
            with PauseManager():
                screenshot = capture_window(window)
        else:
            with PauseManager():
                board.click_cells(moves.special_moves)
                board.click_cells(moves.moves)
                board.click_cells(moves.moves_mines, right_click())
                screenshot = capture_window(window)


        level = board.level
        known = board.known

        end = time.time()
        if end - start < 0.3:
            time.sleep(0.3 - (end - start))
