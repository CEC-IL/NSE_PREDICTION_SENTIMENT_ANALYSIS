
from pathlib import Path
import pandas as pd


# ============================================================
# COMBINE STANDARDIZED NSE DATASETS
# ============================================================
# Purpose:
# Combine the 19 annual standardized NSE datasets into one
# chronological master dataset.
#
# IMPORTANT:
# - Original raw files are not modified.
# - Annual cleaned files are not modified.
# - Annual standardized files are not modified.
# - No records are deleted or corrected.
# - Repeated date/code records are retained.
# ============================================================


# ------------------------------------------------------------
# 1. PROJECT PATHS AND SETTINGS
# ------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = ROOT / "data" / "processed"
REPORT_DIR = ROOT / "reports" / "cleaning"

MASTER_FILE = INPUT_DIR / "nse_master_standardized.csv"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

YEARS = range(2007, 2026)

EXPECTED_COLUMNS = [
    "date",
    "code",
    "name",
    "12m_low",
    "12m_high",
    "day_low",
    "day_high",
    "day_price",
    "previous",
    "change",
    "change_pct",
    "volume",
    "adjusted_price",
]


# ------------------------------------------------------------
# 2. STORAGE
# ------------------------------------------------------------

annual_counts = []
all_datasets = []

total_input_records = 0


# ------------------------------------------------------------
# 3. READ AND CHECK EACH ANNUAL DATASET
# ------------------------------------------------------------

print("=" * 75)
print("COMBINING STANDARDIZED NSE DATASETS")
print("=" * 75)

for year in YEARS:

    file_path = INPUT_DIR / f"{year}_standardized.csv"

    if not file_path.exists():
        raise FileNotFoundError(
            f"Missing annual standardized file: {file_path}"
        )

    df = pd.read_csv(
        file_path,
        dtype={"code": "string"}
    )

    # Check the exact column schema.
    if list(df.columns) != EXPECTED_COLUMNS:
        raise ValueError(
            f"Incorrect schema in {year}_standardized.csv\n"
            f"Expected: {EXPECTED_COLUMNS}\n"
            f"Found: {list(df.columns)}"
        )

    # Convert dates for chronological sorting.
    df["date"] = pd.to_datetime(
        df["date"],
        format="%Y-%m-%d",
        errors="coerce"
    )

    # Do not continue if any date cannot be interpreted.
    invalid_dates = int(df["date"].isna().sum())

    if invalid_dates > 0:
        raise ValueError(
            f"{year} contains {invalid_dates} missing or invalid dates."
        )

    # Internal year field used for reporting only.
    df["_source_year"] = year

    record_count = len(df)

    total_input_records += record_count

    annual_counts.append({
        "year": year,
        "records": record_count
    })

    all_datasets.append(df)

    print(
        f"{year}: {record_count:,} records loaded successfully"
    )


# ------------------------------------------------------------
# 4. COMBINE ALL ANNUAL DATASETS
# ------------------------------------------------------------

print("\nCombining annual datasets...")

master = pd.concat(
    all_datasets,
    ignore_index=True
)

combined_records = len(master)

print(f"Combined records: {combined_records:,}")


# ------------------------------------------------------------
# 5. SORT CHRONOLOGICALLY
# ------------------------------------------------------------

print("Sorting by date and stock code...")

# mergesort is stable, so records sharing the same date and
# stock code retain their relative order from the source files.

master = master.sort_values(
    by=["date", "code"],
    kind="mergesort",
    na_position="last"
).reset_index(drop=True)


# ------------------------------------------------------------
# 6. CHECK COMBINED DATASET INTEGRITY
# ------------------------------------------------------------

if combined_records != total_input_records:
    raise ValueError(
        "Record count mismatch after combining datasets."
    )

if list(master.drop(columns=["_source_year"]).columns) != EXPECTED_COLUMNS:
    raise ValueError(
        "Combined dataset does not have the expected schema."
    )

if master["date"].isna().any():
    raise ValueError(
        "The combined dataset contains missing dates."
    )

if master["code"].isna().any():
    raise ValueError(
        "The combined dataset contains missing stock codes."
    )

# Verify chronological ordering.
if not master["date"].is_monotonic_increasing:
    raise ValueError(
        "The master dataset is not in chronological order."
    )


# ------------------------------------------------------------
# 7. CREATE ANNUAL COVERAGE REPORT
# ------------------------------------------------------------

yearly_summary = (
    master.groupby("_source_year")
    .size()
    .reset_index(name="records")
    .rename(columns={"_source_year": "year"})
)

yearly_summary["year"] = yearly_summary["year"].astype(int)


# ------------------------------------------------------------
# 8. CREATE STOCK COVERAGE REPORT
# ------------------------------------------------------------

stock_summary = (
    master.groupby("code", dropna=False)
    .agg(
        records=("code", "size"),
        first_date=("date", "min"),
        last_date=("date", "max"),
        stock_name=("name", "first")
    )
    .reset_index()
)

stock_summary = stock_summary.sort_values(
    by="code",
    kind="mergesort"
)

stock_summary["first_date"] = (
    stock_summary["first_date"].dt.strftime("%Y-%m-%d")
)

stock_summary["last_date"] = (
    stock_summary["last_date"].dt.strftime("%Y-%m-%d")
)


# ------------------------------------------------------------
# 9. REMOVE INTERNAL REPORTING COLUMN
# ------------------------------------------------------------

master = master.drop(columns=["_source_year"])

# Store dates in the same ISO format used by annual files.
master["date"] = master["date"].dt.strftime("%Y-%m-%d")


# ------------------------------------------------------------
# 10. SAVE MASTER DATASET AND REPORTS
# ------------------------------------------------------------

master.to_csv(
    MASTER_FILE,
    index=False
)

yearly_summary.to_csv(
    REPORT_DIR / "master_dataset_annual_coverage.csv",
    index=False
)

stock_summary.to_csv(
    REPORT_DIR / "master_dataset_stock_coverage.csv",
    index=False
)


# ------------------------------------------------------------
# 11. FINAL VERIFICATION
# ------------------------------------------------------------

# Read the saved master file to verify that it was written
# correctly and that its record count and schema are intact.

saved_master = pd.read_csv(
    MASTER_FILE,
    dtype={"code": "string"}
)

if len(saved_master) != total_input_records:
    raise ValueError(
        "Saved master dataset record count does not match input."
    )

if list(saved_master.columns) != EXPECTED_COLUMNS:
    raise ValueError(
        "Saved master dataset has an incorrect schema."
    )

saved_dates = pd.to_datetime(
    saved_master["date"],
    format="%Y-%m-%d",
    errors="coerce"
)

if saved_dates.isna().any():
    raise ValueError(
        "Saved master dataset contains invalid dates."
    )

if not saved_dates.is_monotonic_increasing:
    raise ValueError(
        "Saved master dataset is not chronologically sorted."
    )


# ------------------------------------------------------------
# 12. FINAL RESULTS
# ------------------------------------------------------------

print("\n" + "=" * 75)
print("MASTER DATASET CREATION COMPLETE")
print("=" * 75)

print(f"Annual files combined: {len(annual_counts)}")
print(f"Total input records: {total_input_records:,}")
print(f"Master dataset records: {len(saved_master):,}")
print(f"Columns: {len(saved_master.columns)}")

print(
    f"First date: {saved_dates.min().strftime('%Y-%m-%d')}"
)

print(
    f"Last date: {saved_dates.max().strftime('%Y-%m-%d')}"
)

print(
    f"Unique stock codes: {saved_master['code'].nunique():,}"
)

print("\nANNUAL RECORD COUNTS:")
print(yearly_summary.to_string(index=False))

print("\nFILES CREATED:")
print(f"1. {MASTER_FILE}")
print("2. reports/cleaning/master_dataset_annual_coverage.csv")
print("3. reports/cleaning/master_dataset_stock_coverage.csv")

print("\nVERIFICATION:")
print("Record count: PASSED")
print("Column schema: PASSED")
print("Date validation: PASSED")
print("Chronological sorting: PASSED")

print("\nNo source datasets were modified.")
print("No records were deleted or corrected.")
