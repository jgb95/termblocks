"""
UI layer: big-digit glyphs, drawing primitives, format utilities, and screen chrome.
"""

from __future__ import annotations

import curses

from .constants import (
    TERMINAL_COLS,
    ROW_TOP_BORDER,
    ROW_CONTENT_START,
    ROW_CONTENT_BOTTOM,
    ROW_PANEL_START,
    ROW_PANEL_END,
    ROW_PANEL_DIVIDER,
    ROW_STATUS,
    ROW_CONTENT_END,
    MAX_VIEWS,
    PANEL_COL_DIV1,
    PANEL_COL_DIV2,
)
from .data import Snapshot


# ============================================================
# Big-digit glyph system
# ============================================================

DIGIT_WIDTH = 6
DIGIT_HEIGHT = 5
CHAR_GAP = 1

_RAW_GLYPHS: dict[str, list[str]] = {
    "0": [" #### ", "##  ##", "##  ##", "##  ##", " #### "],
    "1": ["  ##  ", " ###  ", "  ##  ", "  ##  ", " #### "],
    "2": [" #### ", "##  ##", "   ## ", "  ##  ", "######"],
    "3": [" #### ", "##  ##", "   ## ", "##  ##", " #### "],
    "4": ["##  ##", "##  ##", "######", "    ##", "    ##"],
    "5": ["######", "##    ", "##### ", "    ##", "##### "],
    "6": [" #### ", "##    ", "##### ", "##  ##", " #### "],
    "7": ["######", "    ##", "   ## ", "  ##  ", "  ##  "],
    "8": [" #### ", "##  ##", " #### ", "##  ##", " #### "],
    "9": [" #### ", "##  ##", " #####", "    ##", " #### "],
    ",": ["      ", "      ", "      ", "  ##  ", " ##   "],
    ".": ["      ", "      ", "      ", "      ", "  ##  "],
    ":": ["      ", "  ##  ", "      ", "  ##  ", "      "],
    " ": ["      ", "      ", "      ", "      ", "      "],
    "/": ["     #", "    # ", "   #  ", "  #   ", " #    "],
    "-": ["      ", "      ", " #### ", "      ", "      "],
    "$": [" #####", "## #  ", " #### ", "  # ##", "##### "],
    "%": ["##  # ", "## #  ", "  #   ", " # ## ", "#  ## "],
    "?": [" #### ", "##  ##", "   ## ", "      ", "  ##  "],
}


def build_glyphs(block_char: str = "#", acs_block: int | None = None) -> dict[str, list[str]]:
    """
    Return glyph map with '#' replaced by *block_char*.
    If *acs_block* is given (a curses ACS integer), it is stored under the
    reserved key '__acs__' so draw_big_number can use addch() instead of
    addstr() — ACS integers cannot be embedded in Python strings.
    """
    glyphs: dict[str, list[str]] = {
        k: [row.replace("#", block_char) for row in rows]
        for k, rows in _RAW_GLYPHS.items()
    }
    if acs_block is not None:
        # Store as a single-element list to fit the dict value type
        glyphs["__acs__"] = [str(acs_block)]
    return glyphs


def render_big_text(text: str, glyphs: dict[str, list[str]]) -> list[str]:
    """Render *text* as 5-row big-digit lines using *glyphs*."""
    lines = [""] * DIGIT_HEIGHT
    gap = " " * CHAR_GAP
    for idx, ch in enumerate(text):
        glyph = glyphs.get(ch, glyphs["?"])
        for i in range(DIGIT_HEIGHT):
            if idx > 0:
                lines[i] += gap
            lines[i] += glyph[i]
    return lines


def draw_big_text_acs(
    stdscr: curses.window,
    row: int,
    col: int,
    lines: list[str],
    acs_block: int,
    max_row: int,
    max_col: int,
) -> None:
    """
    Draw pre-rendered big-text lines cell by cell, using addch(acs_block)
    for each '#' sentinel and addstr for runs of spaces.  This is needed
    because ACS characters are large integers that cannot be embedded in
    a Python str for addstr().
    """
    for i, line in enumerate(lines):
        r = row + i
        if r < 0 or r >= max_row:
            continue
        c = col
        for ch in line:
            if c < 0:
                c += 1
                continue
            if c >= max_col:
                break
            try:
                if ch == "#":
                    stdscr.addch(r, c, acs_block)
                else:
                    stdscr.addch(r, c, ord(ch))
            except curses.error:
                pass
            c += 1


# ============================================================
# Low-level curses write helpers
# ============================================================

def safe_addstr(
    stdscr: curses.window,
    row: int,
    col: int,
    text: str,
    max_row: int,
    max_col: int,
) -> None:
    """Write *text* at (row, col), clipping to the screen boundaries."""
    if row < 0 or row >= max_row:
        return
    if col < 0:
        text = text[-col:]
        col = 0
    if not text:
        return
    available = max_col - col
    if available <= 0:
        return
    try:
        stdscr.addstr(row, col, text[:available])
    except curses.error:
        pass


def safe_addstr_inner(
    stdscr: curses.window,
    row: int,
    col: int,
    text: str,
    max_row: int,
    max_col: int,
) -> None:
    """Write *text* clipped to the inner area (inside the 1-char border)."""
    if row < 0 or row >= max_row:
        return
    inner_left = 1
    inner_right = max_col - 2
    if col < inner_left:
        text = text[inner_left - col:]
        col = inner_left
    if not text:
        return
    available = inner_right - col + 1
    if available <= 0:
        return
    try:
        stdscr.addstr(row, col, text[:available])
    except curses.error:
        pass


# ============================================================
# Layout helpers
# ============================================================

def center_col(text_len: int, width: int = TERMINAL_COLS) -> int:
    if text_len >= width:
        return 0
    return (width - text_len) // 2


def draw_centered(
    stdscr: curses.window,
    row: int,
    text: str,
    max_row: int,
    max_col: int,
) -> None:
    col = center_col(len(text), max_col)
    safe_addstr_inner(stdscr, row, col, text, max_row, max_col)


def draw_big_number(
    stdscr: curses.window,
    start_row: int,
    text: str,
    max_row: int,
    max_col: int,
    glyphs: dict[str, list[str]],
) -> None:
    # Check if ACS block rendering was requested (stored by build_glyphs)
    acs_entry = glyphs.get("__acs__")
    if acs_entry is not None:
        acs_block = int(acs_entry[0])
        raw_lines = render_big_text(text, _RAW_GLYPHS)
        text_w = max(len(l) for l in raw_lines)
        col = center_col(text_w, max_col)
        draw_big_text_acs(stdscr, start_row, col, raw_lines, acs_block, max_row, max_col)
    else:
        for i, line in enumerate(render_big_text(text, glyphs)):
            draw_centered(stdscr, start_row + i, line, max_row, max_col)


# ============================================================
# Text formatting utilities
# ============================================================

def format_number(n: float, decimals: int = 0) -> str:
    if decimals > 0:
        return f"{n:,.{decimals}f}"
    return f"{int(n):,}"


def format_hashrate(h: float) -> str:
    if h >= 1e18:
        return f"{h / 1e18:,.2f} EH/s"
    if h >= 1e15:
        return f"{h / 1e15:,.2f} PH/s"
    if h >= 1e12:
        return f"{h / 1e12:,.2f} TH/s"
    return f"{h:,.0f} H/s"


def format_duration(seconds: float) -> str:
    if seconds < 0:
        return "just now"
    d = int(seconds) // 86400
    h = (int(seconds) % 86400) // 3600
    m = (int(seconds) % 3600) // 60
    s = int(seconds) % 60
    if d > 0:
        return f"{d}d {h}h {m}m"
    if h > 0:
        return f"{h}h {m}m {s}s"
    if m > 0:
        return f"{m}m {s}s"
    return f"{s}s"


def progress_bar(fraction: float, width: int = 40) -> str:
    fraction = max(0.0, min(1.0, fraction))
    inner = width - 2
    filled = int(fraction * inner)
    empty = inner - filled
    bar = "=" * filled
    if empty > 0:
        bar += ">"
        empty -= 1
    bar += " " * empty
    return "[" + bar + "]"


# ============================================================
# Screen chrome
# ============================================================

def draw_screen_tabs(
    stdscr: curses.window,
    menu: list[dict],
    screen_idx: int,
    rows: int,
    cols: int,
) -> None:
    """Row 0: top border with screen names rendered as tabs."""
    parts = []
    for i, screen in enumerate(menu):
        if i == screen_idx:
            parts.append(f"[ {screen['name']} ]")
        else:
            parts.append(f"  {screen['name']}  ")
    tab_str = "".join(parts)

    border_inner = cols - 2
    tab_start = max(1, (border_inner - len(tab_str)) // 2)
    remaining = border_inner - tab_start - len(tab_str)

    top = "+" + "-" * tab_start + tab_str
    if remaining > 0:
        top += "-" * remaining
    top += "+"
    safe_addstr(stdscr, ROW_TOP_BORDER, 0, top[:cols], rows, cols)


def draw_content_border(
    stdscr: curses.window,
    rows: int,
    cols: int,
) -> None:
    """Side borders for the content area plus the bottom content divider."""
    for r in range(ROW_CONTENT_START, ROW_CONTENT_BOTTOM):
        safe_addstr(stdscr, r, 0, "|", rows, cols)
        safe_addstr(stdscr, r, cols - 1, "|", rows, cols)
    safe_addstr(
        stdscr, ROW_CONTENT_BOTTOM, 0, "+" + "-" * (cols - 2) + "+", rows, cols
    )


def draw_bottom_panel(
    stdscr: curses.window,
    menu: list[dict],
    screen_idx: int,
    view_idx: int,
    screensaver: bool,
    data: Snapshot,
    rows: int,
    cols: int,
) -> None:
    """
    Bottom panel (rows 17–21): three columns — views | navigate | controls.
    Row 22: divider. Row 23: status line.
    """
    screen = menu[screen_idx]
    views = screen["views"]
    num_views = len(views)

    col_div1 = PANEL_COL_DIV1
    col_div2 = PANEL_COL_DIV2

    # Side and column dividers
    for r in range(ROW_PANEL_START, ROW_PANEL_END + 1):
        safe_addstr(stdscr, r, 0, "|", rows, cols)
        safe_addstr(stdscr, r, col_div1, "|", rows, cols)
        safe_addstr(stdscr, r, col_div2, "|", rows, cols)
        safe_addstr(stdscr, r, cols - 1, "|", rows, cols)

    # --- Views column (cols 1 – col_div1-1) ---
    view_col_width = col_div1 - 1
    for i in range(MAX_VIEWS):
        r = ROW_PANEL_START + i
        if i < num_views:
            name = views[i]["name"]
            entry = f"[{name}]" if i == view_idx else f" {name}"
            entry = entry[:view_col_width].ljust(view_col_width)
        else:
            entry = " " * view_col_width
        safe_addstr(stdscr, r, 1, entry, rows, cols)

    # --- Navigate column (col_div1+1 – col_div2-1) ---
    nav_width = col_div2 - col_div1 - 1
    nav_col = col_div1 + 1
    nav_lines = ["Navigate", "^", "<   >", "v", ""]
    for i, line in enumerate(nav_lines):
        safe_addstr(stdscr, ROW_PANEL_START + i, nav_col, line.center(nav_width), rows, cols)

    # --- Controls column (col_div2+1 – cols-2) ---
    ctrl_width = cols - 1 - col_div2 - 1
    ctrl_col = col_div2 + 1
    ss_label = "ON" if screensaver else "OFF"
    ctrl_lines = [
        "Controls",
        f"[S] Screensaver: {ss_label}",
        "[R] Refresh",
        "[Q] Quit",
        "",
    ]
    for i, line in enumerate(ctrl_lines):
        safe_addstr(stdscr, ROW_PANEL_START + i, ctrl_col, line.center(ctrl_width), rows, cols)

    # --- Divider ---
    safe_addstr(
        stdscr, ROW_PANEL_DIVIDER, 0, "+" + "-" * (cols - 2) + "+", rows, cols
    )

    # --- Status row ---
    if data.last_updated:
        ts = f"Updated: {data.last_updated}"
    else:
        ts = "Fetching data..."
    if data.error:
        ts += f"  [!: {data.error}]"
    inner = ts.center(cols - 2)[: cols - 2]
    try:
        stdscr.addnstr(ROW_STATUS, 0, "|" + inner + "|", cols)
    except curses.error:
        pass
