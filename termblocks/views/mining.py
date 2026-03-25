"""
Mining views: hashrate, difficulty, halving countdown, supply.
"""

from __future__ import annotations

import curses

from ..constants import (
    BIG_NUM_ROW,
    DETAIL1_ROW,
    DETAIL2_ROW,
    DETAIL3_ROW,
    PROGRESS_ROW,
    HALVING_INTERVAL,
    DIFFICULTY_ADJUSTMENT_INTERVAL,
    TARGET_BLOCK_TIME,
    MAX_SUPPLY,
)
from ..data import Snapshot, calc_epoch, calc_subsidy, calc_supply
from ..ui import draw_big_number, draw_centered, format_hashrate, format_number, format_duration, progress_bar


def view_mining_hashrate(
    stdscr: curses.window,
    data: Snapshot,
    rows: int,
    cols: int,
    glyphs: dict,
) -> None:
    if data.hashrate is not None:
        hr_str = format_hashrate(data.hashrate)
        parts = hr_str.rsplit(" ", 1)
        num_str = parts[0].replace(",", "")
        unit_str = parts[1] if len(parts) > 1 else ""
        draw_big_number(stdscr, BIG_NUM_ROW, num_str, rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, f"network hashrate ({unit_str})", rows, cols)
        draw_centered(stdscr, DETAIL2_ROW, "3-day rolling average", rows, cols)
    else:
        draw_big_number(stdscr, BIG_NUM_ROW, "---", rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "network hashrate", rows, cols)


def view_mining_difficulty(
    stdscr: curses.window,
    data: Snapshot,
    rows: int,
    cols: int,
    glyphs: dict,
) -> None:
    height = data.block_height
    if height is not None and data.difficulty is not None:
        # Blocks into and remaining in current 2016-block epoch
        blocks_into_epoch = height % DIFFICULTY_ADJUSTMENT_INTERVAL
        blocks_left = DIFFICULTY_ADJUSTMENT_INTERVAL - blocks_into_epoch
        epoch_num = height // DIFFICULTY_ADJUSTMENT_INTERVAL
        secs_left = blocks_left * TARGET_BLOCK_TIME

        draw_big_number(stdscr, BIG_NUM_ROW, format_number(blocks_left), rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "blocks until difficulty adjustment", rows, cols)
        draw_centered(stdscr, DETAIL2_ROW, f"≈ {format_duration(secs_left)}  ·  epoch {epoch_num}", rows, cols)

        da = data.difficulty_adjustment
        if da:
            change = da.get("difficultyChange", 0)
            t = data.difficulty / 1e12
            draw_centered(stdscr, DETAIL3_ROW, f"est. change: {change:+.2f}%  ·  current: {t:.2f}T", rows, cols)
        else:
            t = data.difficulty / 1e12
            draw_centered(stdscr, DETAIL3_ROW, f"current difficulty: {t:.2f}T", rows, cols)

        progress = blocks_into_epoch / DIFFICULTY_ADJUSTMENT_INTERVAL
        draw_centered(stdscr, PROGRESS_ROW, progress_bar(progress, 50), rows, cols)
    else:
        draw_big_number(stdscr, BIG_NUM_ROW, "---", rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "blocks until difficulty adjustment", rows, cols)


def view_mining_halving(
    stdscr: curses.window,
    data: Snapshot,
    rows: int,
    cols: int,
    glyphs: dict,
) -> None:
    height = data.block_height
    if height is not None:
        epoch = calc_epoch(height)
        next_halving = (epoch + 1) * HALVING_INTERVAL
        blocks_left = next_halving - height
        secs_left = blocks_left * TARGET_BLOCK_TIME
        subsidy = calc_subsidy(height)

        draw_big_number(stdscr, BIG_NUM_ROW, format_number(blocks_left), rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "blocks until next halving", rows, cols)
        draw_centered(stdscr, DETAIL2_ROW, f"≈ {format_duration(secs_left)}  ·  epoch {epoch}", rows, cols)
        draw_centered(stdscr, DETAIL3_ROW, f"current subsidy: {subsidy:.3f} BTC / block", rows, cols)
        progress = (height % HALVING_INTERVAL) / HALVING_INTERVAL
        draw_centered(stdscr, PROGRESS_ROW, progress_bar(progress, 50), rows, cols)
    else:
        draw_big_number(stdscr, BIG_NUM_ROW, "---", rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "blocks until next halving", rows, cols)


def view_mining_supply(
    stdscr: curses.window,
    data: Snapshot,
    rows: int,
    cols: int,
    glyphs: dict,
) -> None:
    height = data.block_height
    if height is not None:
        supply = calc_supply(height)
        pct = (supply / MAX_SUPPLY) * 100
        draw_big_number(stdscr, BIG_NUM_ROW, f"{pct:.1f}%", rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "percentage of total bitcoin supply mined", rows, cols)
        draw_centered(stdscr, DETAIL2_ROW, f"{format_number(supply, 2)} of {format_number(MAX_SUPPLY)} BTC issued", rows, cols)
        draw_centered(stdscr, DETAIL3_ROW, f"{format_number(MAX_SUPPLY - supply, 2)} BTC remaining to mine", rows, cols)
        draw_centered(stdscr, PROGRESS_ROW, progress_bar(supply / MAX_SUPPLY, 50), rows, cols)
    else:
        draw_big_number(stdscr, BIG_NUM_ROW, "---", rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "percentage of total bitcoin supply mined", rows, cols)
