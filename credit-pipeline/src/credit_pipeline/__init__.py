from pathlib import Path

from .bronze import build_bronze
from .silver import build_silver

FILE = Path(__file__).resolve()
PROJECT_ROOT = FILE.parents[2]
DATA = PROJECT_ROOT / "data"
RAW = DATA / "raw"
BRONZE = DATA / "bronze"
SILVER = DATA / "silver"
GOLD = DATA / "gold"
BRONZE_PARQUET = BRONZE / "credit.parquet"
SILVER_PARQUET = SILVER / "credit.parquet"


def main() -> None:
    bronze_df = build_bronze(RAW / "cs-training.csv", BRONZE_PARQUET)
    print(bronze_df.shape[0], "rows saved to", BRONZE_PARQUET)

    silver_df = build_silver(BRONZE_PARQUET, SILVER_PARQUET)
    print(silver_df.shape[0], "rows saved to", SILVER_PARQUET)