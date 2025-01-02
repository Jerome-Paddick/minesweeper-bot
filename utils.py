import os
import time

import keyboard

from window import focus_window


def red_square(image, xy):
    x, y = xy
    for i in range(-5, 5):
        for j in range(-5, 5):
            image.putpixel((x+i, y+j), (255, 0, 0))


def print_grid(grid):
    print("\n")
    # Function to format each cell
    def format_cell(cell):
        if cell is None:
            return "-"  # Represent None as *
        elif isinstance(cell, str):
            return cell  # Left align strings, truncate to 4 chars
        else:
            return str(cell)  # Numbers get a space on each side

    # Print each row
    for row in grid:
        # Join formatted cells with | separators
        formatted_row = " ".join(format_cell(cell) for cell in row)
        print(formatted_row)
    print("\n")


def print_column_colors(image, x_position):
    """Print RGB values for all pixels in a given column."""
    width, height = image.size

    # Make sure x_position is within image bounds
    if x_position < 0 or x_position >= width:
        raise ValueError(f"X position {x_position} is outside image bounds (0-{width - 1})")

    # Get color values for each pixel in the column
    for y in range(height):
        pixel_color = image.getpixel((x_position, y))
        print(f"Y: {y}, Color: RGB{pixel_color}")

def delete_png_files(directory="img"):
    # Check if directory exists
    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist")
        return

    # Count deleted files
    deleted_count = 0

    # Iterate through all files in directory
    for filename in os.listdir(directory):
        if filename.lower().endswith('.png'):
            file_path = os.path.join(directory, filename)
            try:
                os.remove(file_path)
                deleted_count += 1
                print(f"Deleted: {filename}")
            except Exception as e:
                print(f"Error deleting {filename}: {e}")

    # print(f"\nTotal PNG files deleted: {deleted_count}")


class PauseManager:
    def __init__(self, window):
        self.window = window
        self.start = None

    def __enter__(self, *args, **kwargs):
        self.start = time.time()
        focus_window(self.window)
        keyboard.press("F9")
    def __exit__(self, *args, **kwargs):
        end = time.time()
        if end - self.start < 0.2:
            time.sleep(0.2 - (end - self.start))
        keyboard.press("F9")
