from pathlib import Path

import pandas as pd


def build_bronze(raw_csv: Path, out_parquet: Path) -> pd.DataFrame:
    df = pd.read_csv(raw_csv)
    now = pd.Timestamp.now(tz="UTC")
    df['_loaded_at'] = now
    df['_source_file'] = raw_csv.name
    out_parquet.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_parquet, index=False)
    return df