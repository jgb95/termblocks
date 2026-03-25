"""
Constants: configuration, layout row assignments, and content positioning.
"""

# --- Configuration ---
REFRESH_INTERVAL = 10
CYCLE_INTERVAL = 10
MEMPOOL_API = "https://mempool.space/api"
PRICE_API = "https://rate.sx/1btc"

# --- Bitcoin protocol constants ---
HALVING_INTERVAL = 210000
INITIAL_SUBSIDY = 50.0
MAX_SUPPLY = 21_000_000.0
DIFFICULTY_ADJUSTMENT_INTERVAL = 2016
TARGET_BLOCK_TIME = 600  # seconds

# --- Terminal dimensions ---
TERMINAL_COLS = 80
TERMINAL_ROWS = 24

# --- Row assignments (24 rows: 0–23) ---
ROW_TOP_BORDER = 0        # top border with screen tabs
ROW_CONTENT_START = 1     # first content row (inside border)
ROW_CONTENT_END = 15      # last content row (inside border)
ROW_CONTENT_BOTTOM = 16   # horizontal divider below content area
ROW_PANEL_START = 17      # first row of bottom panel
ROW_PANEL_END = 21        # last row of bottom panel  (5 rows: 17–21)
ROW_PANEL_DIVIDER = 22    # horizontal divider below panel
ROW_STATUS = 23           # status / last-updated line (last row)

MAX_VIEWS = 5

# --- Content area row positions (relative to screen rows) ---
# Used by view functions so layout changes only need to happen here.
# All views use the "rich" layout: big number starts at row 4.
BIG_NUM_ROW = 4       # top row of the 5-row big-digit number (rows 4–8)
DETAIL1_ROW = 10      # row 1: always describes what the big number is
DETAIL2_ROW = 12      # row 2: secondary stat (blank row 11 between detail 1)
DETAIL3_ROW = 14      # row 3: tertiary stat or progress bar label (blank row 13 between detail 2)
PROGRESS_ROW = 15     # progress bar row (below detail 3)

# Legacy aliases for any code still using old names
LABEL_ROW = DETAIL1_ROW
SUBLABEL_ROW = 11
DETAIL_ROW = DETAIL2_ROW
DETAIL_ROW2 = DETAIL3_ROW
FOOTER_ROW = PROGRESS_ROW

# --- Bottom panel column dividers ---
PANEL_COL_DIV1 = 26
PANEL_COL_DIV2 = 52
