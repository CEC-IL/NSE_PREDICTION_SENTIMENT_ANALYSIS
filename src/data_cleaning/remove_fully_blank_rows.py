
from pathlib import Path
import pandas as pd

# ============================================================
# 1. PROJECT PATHS AND SETTINGS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"
REPORT_DIR = PROJECT_ROOT / "reports" / "cleaning"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

YEARS = range(2007, 2026)

summary_results = []
removed_rows = []

print("=" * 75)
print("REMOVING COMPLETELY BLANK ROWS")
print("=" * 75)

# ============================================================
# 2. PROCESS ALL ANNUAL CLEANED DATASETS
# ============================================================

for year in YEARS:

    file_path = CLEANED_DIR / f"{year}_cleaned.csv"

    if not file_path.exists():
        print(f"\nWARNING: Missing file: {file_path.name}")
        continue

    df = pd.read_csv(file_path)

    original_count = len(df)

    # Treat empty strings and whitespace-only strings as missing.
    normalized = df.replace(r"^\s*$", pd.NA, regex=True)

    # A row is completely blank only when every column is missing.
    blank_mask = normalized.isna().all(axis=1)

    blank_df = df.loc[blank_mask].copy()
    cleaned_df = df.loc[~blank_mask].copy()

    removed_count = len(blank_df)

    # --------------------------------------------------------
    # SAVE REMOVED ROWS FOR AUDIT
    # --------------------------------------------------------

    for index, row in blank_df.iterrows():
        audit_record = row.to_dict()
        audit_record["year_file"] = year
        audit_record["original_csv_row_number"] = index + 2

        removed_rows.append(audit_record)

    # --------------------------------------------------------
    # SAVE CLEANED DATASET
    # --------------------------------------------------------

    cleaned_df.to_csv(file_path, index=False)

    # --------------------------------------------------------
    # VERIFY OUTPUT
    # --------------------------------------------------------

    verification_df = pd.read_csv(file_path)

    remaining_blank_rows = verification_df.replace(
        r"^\s*$", pd.NA, regex=True
    ).isna().all(axis=1).sum()

    expected_count = original_count - removed_count

    if len(verification_df) != expected_count:
        raise RuntimeError(
            f"Row count verification failed for {year}"
        )

    if remaining_blank_rows != 0:
        raise RuntimeError(
            f"Blank row verification failed for {year}"
        )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    summary_results.append({
        "year": year,
        "original_records": original_count,
        "blank_rows_removed": removed_count,
        "final_records": len(verification_df),
        "remaining_blank_rows": remaining_blank_rows
    })

    print(f"\nYEAR: {year}")
    print(f"Original records: {original_count:,}")
    print(f"Blank rows removed: {removed_count:,}")
    print(f"Final records: {len(verification_df):,}")
    print(f"Remaining blank rows: {remaining_blank_rows}")

# ============================================================
# 3. SAVE AUDIT AND SUMMARY REPORTS
# ============================================================

summary_df = pd.DataFrame(summary_results)

summary_df.to_csv(
    REPORT_DIR / "fully_blank_rows_summary.csv",
    index=False
)

if removed_rows:
    audit_df = pd.DataFrame(removed_rows)
else:
    audit_df = pd.DataFrame(
        columns=["year_file", "original_csv_row_number"]
    )

audit_df.to_csv(
    REPORT_DIR / "fully_blank_rows_removed.csv",
    index=False
)

# ============================================================
# 4. FINAL VERIFICATION
# ============================================================

print("\n" + "=" * 75)
print("BLANK ROW CLEANING COMPLETED")
print("=" * 75)

if not summary_df.empty:
    print(f"Files processed: {len(summary_df)}")
    print(
        f"Original total records: "
        f"{summary_df['original_records'].sum():,}"
    )
    print(
        f"Completely blank rows removed: "
        f"{summary_df['blank_rows_removed'].sum():,}"
    )
    print(
        f"Final total records: "
        f"{summary_df['final_records'].sum():,}"
    )
    print(
        f"Remaining completely blank rows: "
        f"{summary_df['remaining_blank_rows'].sum():,}"
    )

print("\nREPORTS SAVED:")
print("1. fully_blank_rows_summary.csv")
print("2. fully_blank_rows_removed.csv")

print("\nRaw historical files were not modified.")
