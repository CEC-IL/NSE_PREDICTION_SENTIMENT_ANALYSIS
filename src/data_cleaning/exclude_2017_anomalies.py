
from pathlib import Path
import pandas as pd

# ==================================================
# 1. PROJECT PATHS
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "NSE_data_all_stocks_2017.csv"
)

CLEANED_FOLDER = PROJECT_ROOT / "data" / "cleaned"
REPORT_FOLDER = PROJECT_ROOT / "reports" / "cleaning"

CLEANED_FOLDER.mkdir(parents=True, exist_ok=True)
REPORT_FOLDER.mkdir(parents=True, exist_ok=True)

CLEANED_FILE = (
    CLEANED_FOLDER / "2017_after_anomaly_exclusion.csv"
)

EXCLUDED_FILE = (
    REPORT_FOLDER / "2017_excluded_anomalies.csv"
)

# ==================================================
# 2. LOAD ORIGINAL DATA
# ==================================================

print("=" * 70)
print("2017 ANOMALY EXCLUSION")
print("=" * 70)

df = pd.read_csv(RAW_FILE, dtype=str)

original_count = len(df)

print(f"\nOriginal 2017 records: {original_count:,}")

# ==================================================
# 3. IDENTIFY ANOMALOUS RECORDS
# ==================================================

date_column = next(
    column for column in df.columns
    if column.strip().lower() == "date"
)

parsed_dates = pd.to_datetime(
    df[date_column].astype("string").str.strip(),
    format="%d-%b-%y",
    errors="coerce"
)

anomaly_mask = parsed_dates < pd.Timestamp("2017-01-01")

excluded = df.loc[anomaly_mask].copy()
cleaned = df.loc[~anomaly_mask].copy()

excluded_count = len(excluded)
cleaned_count = len(cleaned)

# ==================================================
# 4. SAFETY CHECKS
# ==================================================

print(f"Records identified for exclusion: {excluded_count:,}")
print(f"Records remaining: {cleaned_count:,}")

if excluded_count != 70:
    raise ValueError(
        f"Expected 70 anomalous records, found {excluded_count}. "
        "No output files have been written."
    )

if original_count != excluded_count + cleaned_count:
    raise ValueError(
        "Record count mismatch. No output files have been written."
    )

if cleaned.empty:
    raise ValueError("Cleaned dataset is unexpectedly empty.")

# Confirm no pre-2017 dates remain.
remaining_dates = parsed_dates.loc[~anomaly_mask]

if (remaining_dates < pd.Timestamp("2017-01-01")).any():
    raise ValueError(
        "Pre-2017 records remain in the cleaned dataset."
    )

# ==================================================
# 5. SAVE OUTPUT FILES
# ==================================================

cleaned.to_csv(CLEANED_FILE, index=False)
excluded.to_csv(EXCLUDED_FILE, index=False)

# ==================================================
# 6. VERIFY SAVED FILES
# ==================================================

saved_cleaned = pd.read_csv(CLEANED_FILE, dtype=str)
saved_excluded = pd.read_csv(EXCLUDED_FILE, dtype=str)

assert len(saved_cleaned) == cleaned_count
assert len(saved_excluded) == excluded_count

assert len(saved_cleaned) + len(saved_excluded) == original_count

# ==================================================
# 7. DISPLAY RESULTS
# ==================================================

print("\n" + "=" * 70)
print("EXCLUSION COMPLETED SUCCESSFULLY")
print("=" * 70)

print(f"\nOriginal records: {original_count:,}")
print(f"Excluded records: {excluded_count:,}")
print(f"Remaining records: {cleaned_count:,}")

print("\nOUTPUT FILES:")
print(f"\nCleaned dataset:\n{CLEANED_FILE}")
print(f"\nExcluded records report:\n{EXCLUDED_FILE}")

print("\nVERIFICATION:")
print(f"Saved cleaned records: {len(saved_cleaned):,}")
print(f"Saved excluded records: {len(saved_excluded):,}")
print("All record counts verified.")

print("\nOriginal raw CSV was not modified.")
