import matplotlib.pyplot as plt


def display_grid(grid, highlight_coords=None, highlight_color='red'):
    plt.figure(figsize=(10, 10))

    # Create figure with black background
    ax = plt.gca()
    ax.set_facecolor('black')
    plt.gcf().set_facecolor('black')

    # Plot each cell
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            cell = grid[i][j]
            if cell is None:
                plt.text(j, -i, '-', color='white',
                         ha='center', va='center', fontsize=12)
            else:
                plt.text(j, -i, str(cell), color='white',
                         ha='center', va='center', fontsize=12)

    # If highlight coordinates are provided, color those cells
    if highlight_coords:
        for x, y in highlight_coords:
            rect = plt.Rectangle((y - 0.5, -x - 0.5), 1, 1,
                                 facecolor=highlight_color,
                                 alpha=0.3)
            ax.add_patch(rect)

    # Set the limits
    plt.xlim(-0.5, len(grid[0]) - 0.5)
    plt.ylim(-len(grid) + 0.5, 0.5)

    # Create explicit gridlines
    for x in range(len(grid[0]) + 1):
        plt.axvline(x - 0.5, color='gray', linewidth=1, alpha=0.5)
    for y in range(len(grid) + 1):
        plt.axhline(-y + 0.5, color='gray', linewidth=1, alpha=0.5)

    # Set aspect ratio to make cells square
    ax.set_aspect('equal')

    # Remove axes and ticks
    plt.xticks([])
    plt.yticks([])

    # Remove the border
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Adjust layout
    plt.tight_layout()

    plt.show()


# Example usage:
grid = [
    [None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None],
    [None, None, None, 1, 1, 1, 2, None, None],
    [None, 1, 1, 1, 0, 0, 1, 1, 1],
    [None, 1, 0, 0, 0, 0, 0, 0, 0],
    [None, 1, 1, 1, 1, 0, 0, 0, 0],
    [None, 'M', None, None, 2, 1, 1, 0, 0],
    [None, None, None, None, None, None, 1, 0, 0]
]


if __name__ == "__main__":
    # Display without highlights
    display_grid(grid)

    # Display with some highlighted cells
    highlight_coords = [(4, 1), (4, 2), (4, 3)]  # Row, Column format
    display_grid(grid, highlight_coords, 'red')