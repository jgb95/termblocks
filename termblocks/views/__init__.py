"""
Views package: exports the MENU registry that maps screen/view names to render functions.

Each entry in MENU is a screen dict:
    {
        "name": str,           # tab label shown in the chrome
        "views": [
            {"name": str, "fn": Callable},
            ...
        ]
    }

To add a new view: import its function and append a dict to the appropriate screen's
"views" list (or create a new screen dict).  Nothing else needs to change.
"""

from .price import (
    view_price_usd,
    view_price_gold,
    view_price_silver,
    view_price_sats,
    view_price_marketcap,
)
from .chain import (
    view_chain_height,
    view_chain_lastblock,
    view_chain_utxo,
    view_chain_size,
)
from .lightning import (
    view_ln_capacity_btc,
    view_ln_capacity_usd,
    view_ln_nodes,
    view_ln_channels,
)
from .mempool import (
    view_mempool_fees,
    view_mempool_count,
    view_mempool_live,
)
from .mining import (
    view_mining_hashrate,
    view_mining_difficulty,
    view_mining_halving,
    view_mining_supply,
)

MENU: list[dict] = [
    {
        "name": "Price",
        "views": [
            {"name": "USD",           "fn": view_price_usd},
            {"name": "Gold",          "fn": view_price_gold},
            {"name": "Silver",        "fn": view_price_silver},
            {"name": "Sats per $",    "fn": view_price_sats},
            {"name": "Market Cap",    "fn": view_price_marketcap},
        ],
    },
    {
        "name": "Chain",
        "views": [
            {"name": "Height",        "fn": view_chain_height},
            {"name": "Last Block",    "fn": view_chain_lastblock},
            {"name": "UTXOs",         "fn": view_chain_utxo},
            {"name": "Chain Size",    "fn": view_chain_size},
        ],
    },
    {
        "name": "Lightning",
        "views": [
            {"name": "BTC Capacity",  "fn": view_ln_capacity_btc},
            {"name": "USD Capacity",  "fn": view_ln_capacity_usd},
            {"name": "Nodes",         "fn": view_ln_nodes},
            {"name": "Channels",      "fn": view_ln_channels},
        ],
    },
    {
        "name": "Mempool",
        "views": [
            {"name": "Fees",              "fn": view_mempool_fees},
            {"name": "TX Count",          "fn": view_mempool_count},
            {"name": "Live Transactions", "fn": view_mempool_live},
        ],
    },
    {
        "name": "Mining",
        "views": [
            {"name": "Hashrate",          "fn": view_mining_hashrate},
            {"name": "Difficulty",        "fn": view_mining_difficulty},
            {"name": "Halving",           "fn": view_mining_halving},
            {"name": "Supply",            "fn": view_mining_supply},
        ],
    },
]
