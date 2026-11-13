
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FILE = PROJECT_ROOT / "data" / "raw" / "NSE_data_all_stocks_2017.csv"

df = pd.read_csv(FILE, dtype=str, encoding="utf-8-sig")

df["parsed_date"] = pd.to_datetime(
    df["DATE"].str.strip(),
    format="%d-%b-%y",
    errors="coerce"
)

# Records dated before 2017
before_2017 = df[df["parsed_date"].dt.year < 2017].copy()

print("=" * 75)
print("2017 FILE: HISTORICAL DATE ANOMALY INVESTIGATION")
print("=" * 75)

print("\nTOTAL RECORDS:", len(df))
print("RECORDS BEFORE 2017:", len(before_2017))

print("\nDATE DISTRIBUTION OF RECORDS BEFORE 2017:")

print(
    before_2017["parsed_date"]
    .value_counts()
    .sort_index()
    .to_string()
)

print("\nEARLIEST DATES IN THE FILE:")

print(
    df["parsed_date"]
    .value_counts()
    .sort_index()
    .head(15)
    .to_string()
)

print("\nRECORDS BEFORE 2017 BY COMPANY:")

print(
    before_2017[
        ["DATE", "CODE", "NAME"]
    ].to_string(index=False)
)

print("\nDUPLICATE ROWS AMONG PRE-2017 RECORDS:")

print(before_2017.duplicated().sum())

print("\nREPEATED DATE AND STOCK CODE COMBINATIONS:")

print(
    before_2017.duplicated(
        subset=["DATE", "CODE"],
        keep=False
    ).sum()
)
