
from pathlib import Path
import pandas as pd


# ============================================================
# MARKET-VALUE INTEGRITY VALIDATION
# ============================================================
# Purpose:
# Check whether standardized NSE market values are logically
# consistent across all annual datasets.
#
# IMPORTANT:
# - This script does NOT modify any dataset.
# - It does NOT delete or correct suspicious records.
# - It only identifies records that require investigation.
# ============================================================


# ------------------------------------------------------------
# 1. PROJECT PATHS AND SETTINGS
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = PROJECT_ROOT / "data" / "processed"
REPORT_DIR = PROJECT_ROOT / "reports" / "cleaning"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

YEARS = range(2007, 2026)

# Small tolerance to account for rounding differences.
CHANGE_TOLERANCE = 0.02

# Tolerance for checking whether day_price falls outside
# the reported daily low/high range.
PRICE_RANGE_TOLERANCE = 0.01

PRICE_COLUMNS = [
    "12m_low",
    "12m_high",
    "day_low",
    "day_high",
    "day_price",
    "previous",
    "adjusted_price",
]


# ------------------------------------------------------------
# 2. STORAGE FOR VALIDATION RESULTS
# ------------------------------------------------------------

all_anomalies = []
annual_results = []
zero_volume_results = []


# ------------------------------------------------------------
# 3. FUNCTION TO RECORD SUSPICIOUS RECORDS
# ------------------------------------------------------------

def record_anomalies(
    df,
    mask,
    year,
    issue,
    expected_value=None,
    difference=None
):
    """
    Add records matching a validation rule to the anomaly list.

    Each anomaly retains its original standardized data fields,
    source year, CSV row number, and reason for being flagged.
    """

    flagged = df.loc[mask].copy()

    if flagged.empty:
        return 0

    flagged.insert(0, "source_year", year)

    # CSV row number includes the header row.
    flagged.insert(1, "source_row", flagged.index + 2)

    flagged["issue"] = issue

    flagged["expected_value"] = expected_value
    flagged["difference"] = difference

    all_anomalies.append(flagged)

    return len(flagged)


# ------------------------------------------------------------
# 4. PROCESS ALL ANNUAL DATASETS
# ------------------------------------------------------------

print("=" * 75)
print("MARKET-VALUE INTEGRITY VALIDATION")
print("=" * 75)

total_records = 0
total_anomalies = 0

for year in YEARS:

    file_path = INPUT_DIR / f"{year}_standardized.csv"

    if not file_path.exists():
        raise FileNotFoundError(
            f"Missing standardized dataset: {file_path}"
        )

    df = pd.read_csv(file_path)

    original_count = len(df)
    total_records += original_count

    print(f"\nYEAR: {year}")
    print("-" * 75)
    print(f"Records: {original_count:,}")

    year_anomalies = 0

    # --------------------------------------------------------
    # CHECK 1: NEGATIVE PRICE VALUES
    # --------------------------------------------------------

    for column in PRICE_COLUMNS:

        mask = df[column].notna() & (df[column] < 0)

        count = record_anomalies(
            df=df,
            mask=mask,
            year=year,
            issue=f"negative_{column}"
        )

        year_anomalies += count

    # --------------------------------------------------------
    # CHECK 2: ZERO PRICE VALUES
    # --------------------------------------------------------

    for column in PRICE_COLUMNS:

        mask = df[column].notna() & (df[column] == 0)

        count = record_anomalies(
            df=df,
            mask=mask,
            year=year,
            issue=f"zero_{column}"
        )

        year_anomalies += count

    # --------------------------------------------------------
    # CHECK 3: NEGATIVE TRADING VOLUME
    # --------------------------------------------------------

    mask = df["volume"].notna() & (df["volume"] < 0)

    count = record_anomalies(
        df=df,
        mask=mask,
        year=year,
        issue="negative_volume"
    )

    year_anomalies += count

    # --------------------------------------------------------
    # CHECK 4: DAILY HIGH LOWER THAN DAILY LOW
    # --------------------------------------------------------

    mask = (
        df["day_high"].notna()
        & df["day_low"].notna()
        & (df["day_high"] < df["day_low"])
    )

    count = record_anomalies(
        df=df,
        mask=mask,
        year=year,
        issue="day_high_below_day_low"
    )

    year_anomalies += count

    # --------------------------------------------------------
    # CHECK 5: 12-MONTH HIGH LOWER THAN 12-MONTH LOW
    # --------------------------------------------------------

    mask = (
        df["12m_high"].notna()
        & df["12m_low"].notna()
        & (df["12m_high"] < df["12m_low"])
    )

    count = record_anomalies(
        df=df,
        mask=mask,
        year=year,
        issue="12m_high_below_12m_low"
    )

    year_anomalies += count

    # --------------------------------------------------------
    # CHECK 6: DAY PRICE OUTSIDE DAILY LOW/HIGH RANGE
    # --------------------------------------------------------

    has_daily_range = (
        df["day_price"].notna()
        & df["day_low"].notna()
        & df["day_high"].notna()
    )

    below_low = (
        df["day_price"]
        < df["day_low"] - PRICE_RANGE_TOLERANCE
    )

    above_high = (
        df["day_price"]
        > df["day_high"] + PRICE_RANGE_TOLERANCE
    )

    mask = has_daily_range & (below_low | above_high)

    count = record_anomalies(
        df=df,
        mask=mask,
        year=year,
        issue="day_price_outside_daily_range"
    )

    year_anomalies += count

    # --------------------------------------------------------
    # CHECK 7: CHANGE VS DAY PRICE MINUS PREVIOUS
    # --------------------------------------------------------

    complete_change_data = (
        df["change"].notna()
        & df["day_price"].notna()
        & df["previous"].notna()
    )

    expected_change = df["day_price"] - df["previous"]

    change_difference = df["change"] - expected_change

    mask = (
        complete_change_data
        & (change_difference.abs() > CHANGE_TOLERANCE)
    )

    count = record_anomalies(
        df=df,
        mask=mask,
        year=year,
        issue="change_does_not_match_price_difference",
        expected_value=expected_change,
        difference=change_difference
    )

    year_anomalies += count

    # --------------------------------------------------------
    # INFORMATIONAL CHECK: ZERO TRADING VOLUME
    # --------------------------------------------------------

    zero_volume_count = (
        df["volume"].notna() & (df["volume"] == 0)
    ).sum()

    zero_volume_results.append({
        "year": year,
        "total_records": original_count,
        "zero_volume_records": int(zero_volume_count)
    })

    # --------------------------------------------------------
    # SAVE ANNUAL RESULTS
    # --------------------------------------------------------

    annual_results.append({
        "year": year,
        "total_records": original_count,
        "anomaly_flags": year_anomalies
    })

    total_anomalies += year_anomalies

    print(f"Anomaly flags: {year_anomalies:,}")
    print(f"Zero-volume records (informational): {zero_volume_count:,}")


# ------------------------------------------------------------
# 5. COMBINE ANOMALY RESULTS
# ------------------------------------------------------------

if all_anomalies:

    anomaly_details = pd.concat(
        all_anomalies,
        ignore_index=True
    )

else:

    anomaly_details = pd.DataFrame()


# ------------------------------------------------------------
# 6. CREATE ANNUAL SUMMARY
# ------------------------------------------------------------

annual_summary = pd.DataFrame(annual_results)


# ------------------------------------------------------------
# 7. CREATE ISSUE SUMMARY
# ------------------------------------------------------------

if not anomaly_details.empty:

    issue_summary = (
        anomaly_details
        .groupby(["source_year", "issue"])
        .size()
        .reset_index(name="flagged_records")
        .sort_values(["source_year", "issue"])
    )

    overall_issue_summary = (
        anomaly_details
        .groupby("issue")
        .size()
        .reset_index(name="total_flagged_records")
        .sort_values("total_flagged_records", ascending=False)
    )

else:

    issue_summary = pd.DataFrame(
        columns=["source_year", "issue", "flagged_records"]
    )

    overall_issue_summary = pd.DataFrame(
        columns=["issue", "total_flagged_records"]
    )


# ------------------------------------------------------------
# 8. ZERO-VOLUME SUMMARY
# ------------------------------------------------------------

zero_volume_summary = pd.DataFrame(zero_volume_results)


# ------------------------------------------------------------
# 9. SAVE REPORTS
# ------------------------------------------------------------

annual_summary.to_csv(
    REPORT_DIR / "market_integrity_annual_summary.csv",
    index=False
)

issue_summary.to_csv(
    REPORT_DIR / "market_integrity_issue_summary.csv",
    index=False
)

overall_issue_summary.to_csv(
    REPORT_DIR / "market_integrity_overall_summary.csv",
    index=False
)

anomaly_details.to_csv(
    REPORT_DIR / "market_integrity_anomaly_details.csv",
    index=False
)

zero_volume_summary.to_csv(
    REPORT_DIR / "market_integrity_zero_volume_summary.csv",
    index=False
)


# ------------------------------------------------------------
# 10. FINAL VALIDATION OUTPUT
# ------------------------------------------------------------

print("\n" + "=" * 75)
print("MARKET-VALUE INTEGRITY VALIDATION COMPLETE")
print("=" * 75)

print(f"Annual files processed: {len(annual_summary)}")
print(f"Total records checked: {total_records:,}")
print(f"Total anomaly flags: {total_anomalies:,}")

print("\nANOMALIES BY CATEGORY:")

if not overall_issue_summary.empty:

    print(overall_issue_summary.to_string(index=False))

else:

    print("No anomaly flags found.")

print("\nREPORTS SAVED:")
print("1. market_integrity_annual_summary.csv")
print("2. market_integrity_issue_summary.csv")
print("3. market_integrity_overall_summary.csv")
print("4. market_integrity_anomaly_details.csv")
print("5. market_integrity_zero_volume_summary.csv")

print(f"\nReport folder: {REPORT_DIR}")

print("\nIMPORTANT:")
print("No datasets were modified.")
print("No records were deleted or corrected.")
print("All flagged records require investigation before any decision.")
