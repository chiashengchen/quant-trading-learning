from pathlib import Path

TRADING_DAYS = 252

DEFAULT_PRICE_COL = "close"

DEFAULT_BUY_COST = 0.001
DEFAULT_SELL_COST = 0.0015

DEFAULT_INITIAL_CASH = 100000

# 台股常見券商手續費牌告費率 0.1425%
DEFAULT_FEE_RATE = 0.001425

# 台股股票交易稅，ETF 可能不同，這裡先用股票簡化版
DEFAULT_TAX_RATE = 0.003

ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "outputs"
TABLE_DIR = OUTPUT_DIR / "tables"
FIGURE_DIR = OUTPUT_DIR / "figures"

DB_PATH = DATA_DIR / "quant_data.sqlite"

DATA_DIR.mkdir(parents=True, exist_ok=True)
TABLE_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)