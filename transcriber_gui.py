"""Launcher script for the Transcriber GUI.

Used as the PyInstaller entrypoint or for direct `python transcriber_gui.py` runs.
"""
from ui.main_window import main

if __name__ == '__main__':
    main()
