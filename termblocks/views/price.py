"""
Price views: USD, gold, silver, sats-per-dollar, market cap.
"""

from __future__ import annotations

import curses

from ..constants import (
    BIG_NUM_ROW,
    DETAIL1_ROW,
    DETAIL2_ROW,
    DETAIL3_ROW,
)
from ..data import Snapshot, calc_supply
from ..ui import draw_big_number, draw_centered, format_number


def view_price_usd(
    stdscr: curses.window,
    data: Snapshot,
    rows: int,
    cols: int,
    glyphs: dict,
) -> None:
    if data.price_usd is not None:
        draw_big_number(stdscr, BIG_NUM_ROW, "$" + format_number(data.price_usd), rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "bitcoin price in US dollars", rows, cols)
        if data.price_usd > 0:
            sats = int(100_000_000 / data.price_usd)
            draw_centered(stdscr, DETAIL2_ROW, f"{format_number(sats)} sats per dollar", rows, cols)
    else:
        draw_big_number(stdscr, BIG_NUM_ROW, "---", rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "bitcoin price in US dollars", rows, cols)


def view_price_gold(
    stdscr: curses.window,
    data: Snapshot,
    rows: int,
    cols: int,
    glyphs: dict,
) -> None:
    price = data.price_usd
    gold = data.gold_price_usd
    if price and gold and gold > 0:
        btc_in_gold = price / gold
        draw_big_number(stdscr, BIG_NUM_ROW, f"{btc_in_gold:.1f}", rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "ounces of gold per bitcoin", rows, cols)
        draw_centered(stdscr, DETAIL2_ROW, f"gold spot: ${format_number(gold, 2)} / oz", rows, cols)
    else:
        draw_big_number(stdscr, BIG_NUM_ROW, "---", rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "ounces of gold per bitcoin", rows, cols)


def view_price_silver(
    stdscr: curses.window,
    data: Snapshot,
    rows: int,
    cols: int,
    glyphs: dict,
) -> None:
    price = data.price_usd
    silver = data.silver_price_usd
    if price and silver and silver > 0:
        btc_in_silver = price / silver
        draw_big_number(stdscr, BIG_NUM_ROW, format_number(btc_in_silver), rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "ounces of silver per bitcoin", rows, cols)
        draw_centered(stdscr, DETAIL2_ROW, f"silver spot: ${format_number(silver, 2)} / oz", rows, cols)
    else:
        draw_big_number(stdscr, BIG_NUM_ROW, "---", rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "ounces of silver per bitcoin", rows, cols)


def view_price_sats(
    stdscr: curses.window,
    data: Snapshot,
    rows: int,
    cols: int,
    glyphs: dict,
) -> None:
    if data.price_usd and data.price_usd > 0:
        sats = int(100_000_000 / data.price_usd)
        draw_big_number(stdscr, BIG_NUM_ROW, format_number(sats), rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "satoshis per US dollar", rows, cols)
        draw_centered(stdscr, DETAIL2_ROW, f"1 BTC = ${format_number(data.price_usd, 2)} USD", rows, cols)
    else:
        draw_big_number(stdscr, BIG_NUM_ROW, "---", rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "satoshis per US dollar", rows, cols)


def view_price_marketcap(
    stdscr: curses.window,
    data: Snapshot,
    rows: int,
    cols: int,
    glyphs: dict,
) -> None:
    price = data.price_usd
    height = data.block_height
    if price and height:
        supply = calc_supply(height)
        mcap = price * supply
        if mcap >= 1e12:
            display = f"${mcap / 1e12:.2f}T"
        else:
            display = f"${mcap / 1e9:.1f}B"
        draw_big_number(stdscr, BIG_NUM_ROW, display, rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "bitcoin market capitalization (USD)", rows, cols)
        draw_centered(stdscr, DETAIL2_ROW, f"circulating supply: {format_number(supply, 2)} BTC", rows, cols)
        draw_centered(stdscr, DETAIL3_ROW, f"price: ${format_number(price, 2)} / BTC", rows, cols)
    else:
        draw_big_number(stdscr, BIG_NUM_ROW, "---", rows, cols, glyphs)
        draw_centered(stdscr, DETAIL1_ROW, "bitcoin market capitalization (USD)", rows, cols)
