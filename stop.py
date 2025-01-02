import os
import signal
import keyboard


def signal_handler(signum, frame):
    print("Stopping the loop.")
    os._exit(1)  # Forcefully exit the program


def handle_stop():
    # Handler for the stop signal
    # Set the signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Set up the keyboard hookq
    keyboard.add_hotkey('escape', lambda: os.kill(os.getpid(), signal.SIGINT))
    keyboard.add_hotkey('q', lambda: os.kill(os.getpid(), signal.SIGINT))