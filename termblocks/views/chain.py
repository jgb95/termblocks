"""
Chain views: block height, last block, UTXO set, chain size.
"""

from __future__ import annotations

import curses
import time

from ..constants import (
    BIG_NUM_ROW,
    DETAIL1_ROW,
    DETAIL2_ROW,
    DETAIL3_ROW,
)
from ..data import Snapshot
from ..ui import draw_big_number, draw_centered, format_number, format_duration


def view_chain_height(
    stdscr: curses.window,
    data: Snapshot,
    rows: int,
    cols: int,
    glyphs: dict,
) -> None:
    if data.block_height is not None:
        draw_big_number(stdscr, BIG_NUM_ROW, format_number(data.block_height), rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "current block height", rows, cols)
        if data.last_block_timestamp is not None:
            elapsed = time.time() - data.last_block_timestamp
            draw_centered(stdscr, DETAIL2_ROW, f"last block: {format_duration(elapsed)} ago", rows, cols)
    else:
        draw_big_number(stdscr, BIG_NUM_ROW, "---", rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "current block height", rows, cols)


def view_chain_lastblock(
    stdscr: curses.window,
    data: Snapshot,
    rows: int,
    cols: int,
    glyphs: dict,
) -> None:
    ts = data.last_block_timestamp
    if ts is not None:
        elapsed = time.time() - ts
        mins = int(elapsed) // 60
        secs = int(elapsed) % 60
        if mins < 100:
            draw_big_number(stdscr, BIG_NUM_ROW, f"{mins}:{secs:02d}", rows, cols, glyphs)
            draw_centered(stdscr, DETAIL1_ROW, "time since last block (min : sec)", rows, cols)
        else:
            draw_big_number(stdscr, BIG_NUM_ROW, str(mins), rows, cols, glyphs)
            draw_centered(stdscr, DETAIL1_ROW, "minutes since last block", rows, cols)
            draw_centered(stdscr, DETAIL2_ROW, format_duration(elapsed), rows, cols)
        if data.block_height is not None:
            draw_centered(stdscr, DETAIL2_ROW, f"block #{format_number(data.block_height)}", rows, cols)
    else:
        draw_big_number(stdscr, BIG_NUM_ROW, "---", rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "time since last block", rows, cols)


def view_chain_utxo(
    stdscr: curses.window,
    data: Snapshot,
    rows: int,
    cols: int,
    glyphs: dict,
) -> None:
    if data.utxo_set_size is not None:
        draw_big_number(stdscr, BIG_NUM_ROW, format_number(data.utxo_set_size), rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "unspent transaction outputs (UTXOs)", rows, cols)
    else:
        draw_big_number(stdscr, BIG_NUM_ROW, "---", rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "unspent transaction outputs (UTXOs)", rows, cols)
        draw_centered(stdscr, DETAIL2_ROW, "requires a local node", rows, cols)


def view_chain_size(
    stdscr: curses.window,
    data: Snapshot,
    rows: int,
    cols: int,
    glyphs: dict,
) -> None:
    if data.chain_size is not None:
        gb = data.chain_size / 1e9
        draw_big_number(stdscr, BIG_NUM_ROW, f"{gb:.1f}", rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "blockchain size in gigabytes", rows, cols)
    else:
        draw_big_number(stdscr, BIG_NUM_ROW, "---", rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "blockchain size in gigabytes", rows, cols)
        draw_centered(stdscr, DETAIL2_ROW, "requires a local node", rows, cols)
