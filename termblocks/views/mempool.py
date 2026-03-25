"""
Mempool views: fee rates, TX count, live transactions.
"""

from __future__ import annotations

import curses

from ..constants import (
    BIG_NUM_ROW,
    DETAIL1_ROW,
    DETAIL2_ROW,
    DETAIL3_ROW,
    ROW_CONTENT_END,
)
from ..data import Snapshot
from ..ui import draw_big_number, draw_centered, format_number


def view_mempool_fees(
    stdscr: curses.window,
    data: Snapshot,
    rows: int,
    cols: int,
    glyphs: dict,
) -> None:
    if data.fee_fast is not None:
        draw_big_number(stdscr, BIG_NUM_ROW, str(data.fee_fast), rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "next block fee rate (sat / vB)", rows, cols)
        draw_centered(
            stdscr,
            DETAIL2_ROW,
            f"fast: {data.fee_fast}  *  medium: {data.fee_medium}  *  slow: {data.fee_slow}",
            rows,
            cols,
        )
        if data.mempool_count is not None:
            draw_centered(
                stdscr,
                DETAIL3_ROW,
                f"{format_number(data.mempool_count)} unconfirmed transactions",
                rows,
                cols,
            )
    else:
        draw_big_number(stdscr, BIG_NUM_ROW, "---", rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "next block fee rate (sat / vB)", rows, cols)


def view_mempool_count(
    stdscr: curses.window,
    data: Snapshot,
    rows: int,
    cols: int,
    glyphs: dict,
) -> None:
    if data.mempool_count is not None:
        draw_big_number(stdscr, BIG_NUM_ROW, format_number(data.mempool_count), rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "unconfirmed transactions in the mempool", rows, cols)
        if data.mempool_vsize is not None:
            vmb = data.mempool_vsize / 1e6
            draw_centered(stdscr, DETAIL2_ROW, f"{vmb:.1f} vMB backlog", rows, cols)
        if data.fee_fast is not None:
            draw_centered(
                stdscr,
                DETAIL3_ROW,
                f"fast: {data.fee_fast}  *  medium: {data.fee_medium}  *  slow: {data.fee_slow} sat/vB",
                rows,
                cols,
            )
    else:
        draw_big_number(stdscr, BIG_NUM_ROW, "---", rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "unconfirmed transactions in the mempool", rows, cols)


def view_mempool_live(
    stdscr: curses.window,
    data: Snapshot,
    rows: int,
    cols: int,
    glyphs: dict,
) -> None:
    txs = data.recent_txs
    if txs:
        header = f"{'TXID':<20} {'VALUE':>14} {'sat/vB':>8}"
        draw_centered(stdscr, 2, header, rows, cols)
        draw_centered(stdscr, 3, "-" * 44, rows, cols)
        max_display = min(len(txs), 11)
        for i in range(max_display):
            tx = txs[i]
            txid = tx.get("txid", "")[:16] + ".."
            value = tx.get("value", 0)
            fee = tx.get("fee", 0)
            vsize = tx.get("vsize", 1)
            rate = fee / vsize if vsize > 0 else 0
            val_str = f"{value / 1e8:.4f} BTC" if value >= 1e8 else f"{value:>10,} sat"
            rate_str = f"{rate:.1f}" if rate else "--"
            line = f"{txid:<20} {val_str:>14} {rate_str:>8}"
            row = 4 + i
            if row <= ROW_CONTENT_END:
                draw_centered(stdscr, row, line, rows, cols)
    else:
        draw_big_number(stdscr, BIG_NUM_ROW, "---", rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "waiting for data...", rows, cols)
