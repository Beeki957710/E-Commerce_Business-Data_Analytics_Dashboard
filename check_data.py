
import pandas as pd
from pathlib import Path

folder = Path("data/processed")

files = [
    "order_fact.csv",
    "sales_detail.csv",
    "data_quality_report.csv"
]

for filename in files:
    path = folder / filename

    if not path.exists():
        print(f"MISSING: {filename}")
        continue

    df = pd.read_csv(path)

    print(f"\n{'=' * 45}")
    print(f"File: {filename}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(df.head(3).to_string(index=False))
