import time

from PIL import ImageGrab
from pygetwindow import getAllWindows


def get_window_by_title(title_substring):
    """Find a window by a partial title match."""
    windows = getAllWindows()
    for window in windows:
        if title_substring.lower() in window.title.lower():
            return window
    return None


def focus_window(window):
    """Make the window active and bring it to front."""
    if window:
        if window.isMinimized:
            window.restore()
        window.activate()


def capture_window(window):
    """Capture a screenshot of a specific window."""
    if window.isMinimized:
        window.restore()
    # Give the window a moment to restore
    time.sleep(0.2)

    # Get the window boundaries
    left, top = window.left, window.top
    width, height = window.width, window.height

    # Capture the region
    screenshot = ImageGrab.grab(bbox=(left, top, left + width, top + height))
    return screenshot