"""
Lightning views: capacity (BTC and USD), nodes, channels.
"""

from __future__ import annotations

import curses

from ..constants import BIG_NUM_ROW, DETAIL1_ROW, DETAIL2_ROW, DETAIL3_ROW
from ..data import Snapshot
from ..ui import draw_big_number, draw_centered, format_number


def view_ln_capacity_btc(
    stdscr: curses.window,
    data: Snapshot,
    rows: int,
    cols: int,
    glyphs: dict,
) -> None:
    if data.ln_capacity_btc is not None:
        draw_big_number(stdscr, BIG_NUM_ROW, format_number(data.ln_capacity_btc), rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "lightning network capacity (BTC)", rows, cols)
        if data.price_usd is not None:
            usd = data.ln_capacity_btc * data.price_usd
            if usd >= 1e9:
                usd_str = f"${usd / 1e9:.2f}B USD"
            elif usd >= 1e6:
                usd_str = f"${usd / 1e6:.1f}M USD"
            else:
                usd_str = f"${format_number(usd)} USD"
            draw_centered(stdscr, DETAIL2_ROW, f"~{usd_str}", rows, cols)
        if data.ln_num_nodes is not None and data.ln_num_channels is not None:
            draw_centered(stdscr, DETAIL3_ROW, f"{format_number(data.ln_num_nodes)} nodes  *  {format_number(data.ln_num_channels)} channels", rows, cols)
    else:
        draw_big_number(stdscr, BIG_NUM_ROW, "---", rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "lightning network capacity (BTC)", rows, cols)


def view_ln_capacity_usd(
    stdscr: curses.window,
    data: Snapshot,
    rows: int,
    cols: int,
    glyphs: dict,
) -> None:
    cap = data.ln_capacity_btc
    price = data.price_usd
    if cap is not None and price is not None:
        usd = cap * price
        if usd >= 1e9:
            display = f"${usd / 1e9:.2f}B"
        elif usd >= 1e6:
            display = f"${usd / 1e6:.1f}M"
        else:
            display = "$" + format_number(usd)
        draw_big_number(stdscr, BIG_NUM_ROW, display, rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "lightning network capacity (USD)", rows, cols)
        draw_centered(stdscr, DETAIL2_ROW, f"{format_number(cap)} BTC locked", rows, cols)
        if data.ln_num_nodes is not None and data.ln_num_channels is not None:
            draw_centered(stdscr, DETAIL3_ROW, f"{format_number(data.ln_num_nodes)} nodes  *  {format_number(data.ln_num_channels)} channels", rows, cols)
    else:
        draw_big_number(stdscr, BIG_NUM_ROW, "---", rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "lightning network capacity (USD)", rows, cols)


def view_ln_nodes(
    stdscr: curses.window,
    data: Snapshot,
    rows: int,
    cols: int,
    glyphs: dict,
) -> None:
    if data.ln_num_nodes is not None:
        draw_big_number(stdscr, BIG_NUM_ROW, format_number(data.ln_num_nodes), rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "lightning network nodes", rows, cols)
        if data.ln_num_channels is not None:
            draw_centered(stdscr, DETAIL2_ROW, f"{format_number(data.ln_num_channels)} channels open", rows, cols)
    else:
        draw_big_number(stdscr, BIG_NUM_ROW, "---", rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "lightning network nodes", rows, cols)


def view_ln_channels(
    stdscr: curses.window,
    data: Snapshot,
    rows: int,
    cols: int,
    glyphs: dict,
) -> None:
    if data.ln_num_channels is not None:
        draw_big_number(stdscr, BIG_NUM_ROW, format_number(data.ln_num_channels), rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "lightning network channels", rows, cols)
        if data.ln_num_nodes is not None:
            draw_centered(stdscr, DETAIL2_ROW, f"across {format_number(data.ln_num_nodes)} nodes", rows, cols)
    else:
        draw_big_number(stdscr, BIG_NUM_ROW, "---", rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "lightning network channels", rows, cols)
