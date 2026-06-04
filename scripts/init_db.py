import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from database import init_db


def main():
    init_db()
    print("Database initialized.")


if __name__ == "__main__":
    main()