"""
Entry point: `python -m termblocks`

Main loop responsibilities:
  - Start the BitcoinData background thread.
  - Handle keyboard input (navigation, screensaver toggle, refresh, quit).
  - Drive the view cycle timer.
  - Delegate all rendering to ui.py and the active view function.
"""

from __future__ import annotations

import curses
import time

from .constants import (
    CYCLE_INTERVAL,
    DEFAULT_BLOCK_CHAR,
    TERMINAL_COLS,
    TERMINAL_ROWS,
)
from .data import BitcoinData
from .ui import (
    build_glyphs,
    draw_screen_tabs,
    draw_content_border,
    draw_bottom_panel,
)
from .views import MENU


# ============================================================
# Screensaver
# ============================================================

def run_screensaver(stdscr: curses.window, rows: int, cols: int, glyphs: dict) -> None:
    """Simple moving-block screensaver; exits on any keypress."""
    from .ui import render_big_text, safe_addstr
    import math

    text = "TERMBLOCKS"
    rendered = render_big_text(text, glyphs)
    text_w = max(len(l) for l in rendered)
    text_h = len(rendered)

    x = (cols - text_w) // 2
    y = (rows - text_h) // 2
    dx, dy = 1, 1

    stdscr.nodelay(True)
    stdscr.timeout(50)

    while True:
        ch = stdscr.getch()
        if ch != curses.ERR:
            break

        stdscr.erase()
        for i, line in enumerate(rendered):
            safe_addstr(stdscr, y + i, x, line, rows, cols)
        stdscr.refresh()

        x += dx
        y += dy
        if x <= 0 or x + text_w >= cols:
            dx = -dx
        if y <= 0 or y + text_h >= rows:
            dy = -dy
        time.sleep(0.05)


# ============================================================
# Main curses loop
# ============================================================

def main(stdscr: curses.window) -> None:
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(200)

    glyphs = build_glyphs(DEFAULT_BLOCK_CHAR)

    bitcoin = BitcoinData()
    bitcoin.start()

    screen_idx = 0
    view_idx = 0
    screensaver = False
    last_cycle = time.monotonic()

    rows, cols = TERMINAL_ROWS, TERMINAL_COLS

    while True:
        # --- Input handling ---
        ch = stdscr.getch()

        if ch in (ord("q"), ord("Q")):
            bitcoin.stop()
            break

        elif ch in (ord("s"), ord("S")):
            screensaver = not screensaver

        elif ch in (ord("r"), ord("R")):
            bitcoin.request_refresh()

        elif ch == curses.KEY_LEFT:
            screen_idx = (screen_idx - 1) % len(MENU)
            view_idx = 0
            last_cycle = time.monotonic()

        elif ch == curses.KEY_RIGHT:
            screen_idx = (screen_idx + 1) % len(MENU)
            view_idx = 0
            last_cycle = time.monotonic()

        elif ch == curses.KEY_UP:
            num_views = len(MENU[screen_idx]["views"])
            view_idx = (view_idx - 1) % num_views
            last_cycle = time.monotonic()

        elif ch == curses.KEY_DOWN:
            num_views = len(MENU[screen_idx]["views"])
            view_idx = (view_idx + 1) % num_views
            last_cycle = time.monotonic()

        # --- Screensaver ---
        if screensaver:
            run_screensaver(stdscr, rows, cols, glyphs)
            screensaver = False
            stdscr.nodelay(True)
            stdscr.timeout(200)
            continue

        # --- Auto-cycle views ---
        now = time.monotonic()
        if now - last_cycle >= CYCLE_INTERVAL:
            num_views = len(MENU[screen_idx]["views"])
            view_idx = (view_idx + 1) % num_views
            last_cycle = now

        # --- Render ---
        data = bitcoin.snapshot()
        stdscr.erase()

        draw_screen_tabs(stdscr, MENU, screen_idx, rows, cols)
        draw_content_border(stdscr, rows, cols)

        view_fn = MENU[screen_idx]["views"][view_idx]["fn"]
        view_fn(stdscr, data, rows, cols, glyphs)

        draw_bottom_panel(
            stdscr, MENU, screen_idx, view_idx, screensaver, data, rows, cols
        )

        stdscr.refresh()


# ============================================================
# Entry
# ============================================================

def run() -> None:
    curses.wrapper(main)


if __name__ == "__main__":
    run()
