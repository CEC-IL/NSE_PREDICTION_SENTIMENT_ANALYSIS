
from pathlib import Path
import pandas as pd


# ============================================================
# INVESTIGATE MARKET INTEGRITY FLAGS
# ============================================================
# Purpose:
# Display the 13 records flagged by the previous validation.
#
# This script is read-only. It does not modify datasets.
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPORT_DIR = PROJECT_ROOT / "reports" / "cleaning"

INPUT_FILE = (
    REPORT_DIR / "market_integrity_anomaly_details.csv"
)

df = pd.read_csv(INPUT_FILE)

print("=" * 75)
print("INVESTIGATION OF MARKET INTEGRITY FLAGS")
print("=" * 75)

print(f"\nTotal flagged records: {len(df)}")

if df.empty:
    print("\nNo flagged records found.")
    raise SystemExit


# ------------------------------------------------------------
# 1. DISPLAY FLAG COUNTS BY YEAR AND ISSUE
# ------------------------------------------------------------

print("\nFLAGS BY YEAR AND ISSUE")
print("-" * 75)

print(
    df.groupby(["source_year", "issue"])
    .size()
    .reset_index(name="count")
    .to_string(index=False)
)


# ------------------------------------------------------------
# 2. DISPLAY RELEVANT RECORD DETAILS
# ------------------------------------------------------------

columns_to_display = [
    "source_year",
    "source_row",
    "date",
    "code",
    "name",
    "issue",
    "12m_low",
    "12m_high",
    "day_low",
    "day_high",
    "day_price",
    "previous",
    "change",
    "expected_value",
    "difference",
    "volume",
    "adjusted_price",
]

available_columns = [
    column for column in columns_to_display
    if column in df.columns
]

print("\nFLAGGED RECORD DETAILS")
print("-" * 75)

for issue in df["issue"].dropna().unique():

    issue_df = df[df["issue"] == issue]

    print(f"\nISSUE: {issue}")
    print("-" * 75)

    print(
        issue_df[available_columns]
        .to_string(index=False)
    )


# ------------------------------------------------------------
# 3. SAVE A READABLE INVESTIGATION REPORT
# ------------------------------------------------------------

output_file = (
    REPORT_DIR / "market_integrity_investigation.csv"
)

df[available_columns].to_csv(
    output_file,
    index=False
)

print("\n" + "=" * 75)
print("INVESTIGATION COMPLETE")
print("=" * 75)

print(f"Records investigated: {len(df)}")
print(f"Investigation report: {output_file}")

print("\nNo datasets were modified.")
