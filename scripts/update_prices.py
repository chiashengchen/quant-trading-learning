import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from data_service import update_stock_data


STOCK_IDS = ["0050", "2330", "2317", "2454", "2303"]

START_DATE = "2015-01-01"
END_DATE = datetime.today().strftime("%Y-%m-%d")


def main():
    for stock_id in STOCK_IDS:
        print(f"\nUpdating {stock_id}")
        update_stock_data(stock_id, START_DATE, END_DATE)


if __name__ == "__main__":
    main()