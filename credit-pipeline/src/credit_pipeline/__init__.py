from pathlib import Path

from .bronze import build_bronze

FILE = Path(__file__).resolve()
PROJECT_ROOT = FILE.parents[2]
DATA = PROJECT_ROOT / "data"
RAW = DATA / "raw"
BRONZE = DATA / "bronze"
SILVER = DATA / "silver"
GOLD = DATA / "gold"
BRONZE_PARQUET = BRONZE / "credit.parquet"


def main() -> None:
    df = build_bronze(RAW / "cs-training.csv", BRONZE_PARQUET)
    print(df.shape[0], "rows saved to", BRONZE_PARQUET)