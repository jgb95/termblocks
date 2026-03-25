"""
Data layer: Snapshot dataclass and BitcoinData background fetcher.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any

import requests

from .constants import (
    REFRESH_INTERVAL,
    MEMPOOL_API,
    PRICE_API,
    HALVING_INTERVAL,
    INITIAL_SUBSIDY,
    MAX_SUPPLY,
)


# ============================================================
# Snapshot dataclass
# ============================================================

@dataclass
class Snapshot:
    price_usd: float | None = None
    gold_price_usd: float | None = None
    silver_price_usd: float | None = None
    block_height: int | None = None
    last_block_timestamp: float | None = None
    chain_size: int | None = None
    utxo_set_size: int | None = None
    ln_capacity_btc: float | None = None
    ln_num_nodes: int | None = None
    ln_num_channels: int | None = None
    mempool_count: int | None = None
    mempool_vsize: int | None = None
    fee_fast: int | None = None
    fee_medium: int | None = None
    fee_slow: int | None = None
    recent_txs: list[dict[str, Any]] = field(default_factory=list)
    hashrate: float | None = None
    difficulty: float | None = None
    difficulty_adjustment: dict[str, Any] | None = None
    last_updated: str | None = None
    error: str | None = None


# ============================================================
# Bitcoin math helpers
# ============================================================

def calc_epoch(height: int) -> int:
    return height // HALVING_INTERVAL


def calc_subsidy(height: int) -> float:
    return INITIAL_SUBSIDY / (2 ** calc_epoch(height))


def calc_supply(height: int) -> float:
    supply = 0.0
    remaining = height
    epoch = 0
    while remaining > 0:
        subsidy = INITIAL_SUBSIDY / (2 ** epoch)
        blocks_used = min(remaining, HALVING_INTERVAL)
        supply += blocks_used * subsidy
        remaining -= blocks_used
        epoch += 1
    return supply


# ============================================================
# BitcoinData — background fetch thread
# ============================================================

class BitcoinData:
    def __init__(
        self,
        refresh_interval: int = REFRESH_INTERVAL,
        mempool_api: str = MEMPOOL_API,
        price_api: str = PRICE_API,
    ) -> None:
        self._refresh_interval = refresh_interval
        self._mempool_api = mempool_api
        self._price_api = price_api

        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._early_refresh = threading.Event()
        self._thread: threading.Thread | None = None

        self._state = Snapshot()

    # ----------------------------------------------------------
    # Public API
    # ----------------------------------------------------------

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def request_refresh(self) -> None:
        """Signal the background thread to refresh immediately."""
        self._early_refresh.set()

    def snapshot(self) -> Snapshot:
        """Return a copy of the current state (thread-safe)."""
        with self._lock:
            import copy
            return copy.copy(self._state)

    # ----------------------------------------------------------
    # Background run loop
    # ----------------------------------------------------------

    def _run(self) -> None:
        while not self._stop.is_set():
            self._fetch_all()
            # Wait for either the refresh interval or an early-refresh signal.
            self._early_refresh.wait(timeout=self._refresh_interval)
            self._early_refresh.clear()

    # ----------------------------------------------------------
    # Individual fetch methods
    # ----------------------------------------------------------

    def _fetch_price(self, errors: list[str]) -> None:
        try:
            resp = requests.get(
                self._price_api, headers={"User-Agent": "curl"}, timeout=10
            )
            resp.raise_for_status()
            with self._lock:
                self._state.price_usd = float(resp.text.strip())
        except Exception:
            errors.append("Price")

    def _fetch_precious_metals(self, _errors: list[str]) -> None:
        try:
            resp = requests.get(
                "https://data-asg.goldprice.org/dbXRates/USD",
                timeout=10,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                    "Origin": "https://goldprice.org",
                    "Referer": "https://goldprice.org/",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            if "items" in data and data["items"]:
                item = data["items"][0]
                with self._lock:
                    self._state.gold_price_usd = float(item.get("xauPrice", 0))
                    self._state.silver_price_usd = float(item.get("xagPrice", 0))
        except Exception:
            pass  # non-critical; no error label shown

    def _fetch_height(self, errors: list[str]) -> None:
        try:
            resp = requests.get(
                f"{self._mempool_api}/blocks/tip/height", timeout=10
            )
            resp.raise_for_status()
            with self._lock:
                self._state.block_height = int(resp.text.strip())
        except Exception:
            errors.append("Height")

    def _fetch_last_block(self, errors: list[str]) -> None:
        try:
            resp = requests.get(f"{self._mempool_api}/blocks", timeout=10)
            resp.raise_for_status()
            blocks = resp.json()
            if blocks:
                with self._lock:
                    self._state.last_block_timestamp = blocks[0].get("timestamp")
        except Exception:
            errors.append("Blocks")

    def _fetch_mining(self, errors: list[str]) -> None:
        try:
            resp = requests.get(
                f"{self._mempool_api}/v1/mining/hashrate/3d", timeout=10
            )
            resp.raise_for_status()
            data = resp.json()
            with self._lock:
                if data.get("hashrates"):
                    self._state.hashrate = float(
                        data["hashrates"][-1].get("avgHashrate", 0)
                    )
                if data.get("difficulty"):
                    self._state.difficulty = float(
                        data["difficulty"][-1].get("difficulty", 0)
                    )
                elif data.get("currentDifficulty"):
                    self._state.difficulty = float(data["currentDifficulty"])
        except Exception:
            errors.append("Mining")

    def _fetch_difficulty_adjustment(self, _errors: list[str]) -> None:
        try:
            resp = requests.get(
                f"{self._mempool_api}/v1/difficulty-adjustment", timeout=10
            )
            resp.raise_for_status()
            with self._lock:
                self._state.difficulty_adjustment = resp.json()
        except Exception:
            pass  # non-critical

    def _fetch_mempool(self, errors: list[str]) -> None:
        try:
            resp = requests.get(f"{self._mempool_api}/mempool", timeout=10)
            resp.raise_for_status()
            data = resp.json()
            with self._lock:
                self._state.mempool_count = data.get("count", 0)
                self._state.mempool_vsize = data.get("vsize", 0)
        except Exception:
            errors.append("Mempool")

    def _fetch_fees(self, errors: list[str]) -> None:
        try:
            resp = requests.get(
                f"{self._mempool_api}/v1/fees/recommended", timeout=10
            )
            resp.raise_for_status()
            data = resp.json()
            with self._lock:
                self._state.fee_fast = data.get("fastestFee", 0)
                self._state.fee_medium = data.get("halfHourFee", 0)
                self._state.fee_slow = data.get("hourFee", 0)
        except Exception:
            errors.append("Fees")

    def _fetch_recent_txs(self, _errors: list[str]) -> None:
        try:
            resp = requests.get(
                f"{self._mempool_api}/mempool/recent", timeout=10
            )
            resp.raise_for_status()
            with self._lock:
                self._state.recent_txs = resp.json()[:10]
        except Exception:
            pass  # non-critical

    def _fetch_lightning(self, errors: list[str]) -> None:
        try:
            resp = requests.get(
                f"{self._mempool_api}/v1/lightning/statistics/latest", timeout=10
            )
            resp.raise_for_status()
            data = resp.json()
            latest = data.get("latest", data)
            with self._lock:
                cap_sat = int(latest.get("total_capacity", 0))
                self._state.ln_capacity_btc = cap_sat / 1e8
                self._state.ln_num_nodes = int(
                    latest.get(
                        "node_count",
                        latest.get("tor_nodes", 0) + latest.get("clearnet_nodes", 0),
                    )
                )
                self._state.ln_num_channels = int(latest.get("channel_count", 0))
        except Exception:
            errors.append("Lightning")

    # ----------------------------------------------------------
    # Coordinated fetch
    # ----------------------------------------------------------

    def _fetch_all(self) -> None:
        errors: list[str] = []

        self._fetch_price(errors)
        self._fetch_precious_metals(errors)
        self._fetch_height(errors)
        self._fetch_last_block(errors)
        self._fetch_mining(errors)
        self._fetch_difficulty_adjustment(errors)
        self._fetch_mempool(errors)
        self._fetch_fees(errors)
        self._fetch_recent_txs(errors)
        self._fetch_lightning(errors)

        with self._lock:
            self._state.last_updated = time.strftime("%Y-%m-%d %H:%M:%S")
            self._state.error = ", ".join(errors) if errors else None
