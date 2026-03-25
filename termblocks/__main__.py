"""
Entry point: `python -m termblocks`

Main loop responsibilities:
  - Start the BitcoinData background thread.
  - Handle keyboard input (navigation, screensaver toggle, refresh, quit).
  - Drive the screensaver/view cycle timer.
  - Delegate all rendering to ui.py and the active view function.
"""

from __future__ import annotations

import curses
import time

from .constants import (
    CYCLE_INTERVAL,
    TERMINAL_COLS,
    TERMINAL_ROWS,
)
from .data import BitcoinData
from .ui import (
    build_glyphs,
    draw_screen_tabs,
    draw_content_border,
    draw_bottom_panel,
    draw_centered,
)
from .views import MENU


# ============================================================
# Build a flat ordered list of all (screen_idx, view_idx) pairs
# ============================================================

def _build_screensaver_sequence() -> list[tuple[int, int]]:
    """Return every (screen_idx, view_idx) pair in order, for screensaver cycling."""
    seq: list[tuple[int, int]] = []
    for si, screen in enumerate(MENU):
        for vi in range(len(screen["views"])):
            seq.append((si, vi))
    return seq


_SS_SEQUENCE = _build_screensaver_sequence()


# ============================================================
# Main curses loop
# ============================================================

def main(stdscr: curses.window) -> None:
    try:
        curses.curs_set(0)
    except curses.error:
        pass  # Terminal doesn't support hiding the cursor (e.g. TVI925)
    stdscr.nodelay(True)
    stdscr.timeout(200)

    glyphs = build_glyphs()

    bitcoin = BitcoinData()
    bitcoin.start()

    screen_idx = 0
    view_idx = 0
    screensaver = False
    last_cycle = time.monotonic()

    # Index into _SS_SEQUENCE for screensaver cycling
    ss_seq_idx = 0

    rows, cols = TERMINAL_ROWS, TERMINAL_COLS

    while True:
        # --- Input handling ---
        ch = stdscr.getch()

        if ch in (ord("q"), ord("Q")):
            bitcoin.stop()
            break

        elif ch in (ord("s"), ord("S")):
            screensaver = not screensaver
            if screensaver:
                # Initialise screensaver position to match current view
                for i, (si, vi) in enumerate(_SS_SEQUENCE):
                    if si == screen_idx and vi == view_idx:
                        ss_seq_idx = i
                        break
            last_cycle = time.monotonic()

        elif ch in (ord("r"), ord("R")):
            bitcoin.request_refresh()

        elif ch in (curses.KEY_LEFT, ord("h"), ord("H")):
            if screensaver:
                screensaver = False
            screen_idx = (screen_idx - 1) % len(MENU)
            view_idx = 0
            last_cycle = time.monotonic()

        elif ch in (curses.KEY_RIGHT, ord("l"), ord("L")):
            if screensaver:
                screensaver = False
            screen_idx = (screen_idx + 1) % len(MENU)
            view_idx = 0
            last_cycle = time.monotonic()

        elif ch in (curses.KEY_UP, ord("k"), ord("K")):
            if screensaver:
                screensaver = False
            num_views = len(MENU[screen_idx]["views"])
            view_idx = (view_idx - 1) % num_views
            last_cycle = time.monotonic()

        elif ch in (curses.KEY_DOWN, ord("j"), ord("J")):
            if screensaver:
                screensaver = False
            num_views = len(MENU[screen_idx]["views"])
            view_idx = (view_idx + 1) % num_views
            last_cycle = time.monotonic()

        # --- Screensaver auto-cycle ---
        now = time.monotonic()
        if screensaver and now - last_cycle >= CYCLE_INTERVAL:
            ss_seq_idx = (ss_seq_idx + 1) % len(_SS_SEQUENCE)
            screen_idx, view_idx = _SS_SEQUENCE[ss_seq_idx]
            last_cycle = now

        # --- Render ---
        data = bitcoin.snapshot()
        stdscr.erase()

        if screensaver:
            # Minimal screensaver UI: just a title line and the view content
            screen_name = MENU[screen_idx]["name"]
            view_name = MENU[screen_idx]["views"][view_idx]["name"]
            title = f"{screen_name} > {view_name}"
            draw_centered(stdscr, 0, title, rows, cols)
        else:
            draw_screen_tabs(stdscr, MENU, screen_idx, rows, cols)
            draw_content_border(stdscr, rows, cols)

        view_fn = MENU[screen_idx]["views"][view_idx]["fn"]
        view_fn(stdscr, data, rows, cols, glyphs)

        if not screensaver:
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
