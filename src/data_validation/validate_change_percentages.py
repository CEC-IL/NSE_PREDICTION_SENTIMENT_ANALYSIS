
from pathlib import Path
import pandas as pd


# ============================================================
# CHANGE PERCENTAGE VALIDATION
# ============================================================
# Purpose:
# Compare the source Change% column against:
#
# (Change / Previous) * 100
#
# This script only investigates values.
# It does not modify any datasets.
# ============================================================


ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT / "data" / "processed"
REPORT_DIR = ROOT / "reports" / "cleaning"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

YEARS = range(2007, 2026)

# Allow a small difference caused by rounding.
TOLERANCE = 0.05

all_results = []
annual_summary = []


print("=" * 75)
print("CHANGE PERCENTAGE VALIDATION")
print("=" * 75)


# ------------------------------------------------------------
# PROCESS ALL YEARS
# ------------------------------------------------------------

for year in YEARS:

    file_path = DATA_DIR / f"{year}_standardized.csv"

    df = pd.read_csv(file_path)

    # Only records with all required values can be checked.
    eligible = (
        df["change"].notna()
        & df["previous"].notna()
        & df["change_pct"].notna()
        & (df["previous"] != 0)
    )

    checked = df.loc[eligible].copy()

    expected_pct = (
        checked["change"] / checked["previous"]
    ) * 100

    difference = checked["change_pct"] - expected_pct

    # Identify discrepancies beyond the rounding tolerance.
    mismatch = difference.abs() > TOLERANCE

    flagged = checked.loc[mismatch].copy()

    if not flagged.empty:

        flagged.insert(0, "source_year", year)
        flagged.insert(1, "source_row", flagged.index + 2)

        flagged["expected_change_pct"] = expected_pct.loc[
            mismatch
        ]

        flagged["percentage_difference"] = difference.loc[
            mismatch
        ]

        all_results.append(flagged)

    mismatch_count = int(mismatch.sum())

    annual_summary.append({
        "year": year,
        "total_records": len(df),
        "eligible_records": len(checked),
        "records_not_checked": len(df) - len(checked),
        "percentage_mismatches": mismatch_count,
        "mismatch_rate_pct": (
            mismatch_count / len(checked) * 100
            if len(checked) > 0 else 0
        )
    })

    print(f"\nYEAR: {year}")
    print("-" * 75)
    print(f"Total records: {len(df):,}")
    print(f"Eligible records: {len(checked):,}")
    print(f"Percentage mismatches: {mismatch_count:,}")


# ------------------------------------------------------------
# COMBINE RESULTS
# ------------------------------------------------------------

if all_results:
    mismatch_details = pd.concat(
        all_results,
        ignore_index=True
    )
else:
    mismatch_details = pd.DataFrame()


summary = pd.DataFrame(annual_summary)


# ------------------------------------------------------------
# SAVE REPORTS
# ------------------------------------------------------------

summary.to_csv(
    REPORT_DIR / "change_percentage_annual_summary.csv",
    index=False
)

mismatch_details.to_csv(
    REPORT_DIR / "change_percentage_mismatches.csv",
    index=False
)


# ------------------------------------------------------------
# OVERALL RESULTS
# ------------------------------------------------------------

total_checked = summary["eligible_records"].sum()

total_mismatches = summary["percentage_mismatches"].sum()

print("\n" + "=" * 75)
print("CHANGE PERCENTAGE VALIDATION COMPLETE")
print("=" * 75)

print(f"Annual files processed: {len(summary)}")
print(f"Eligible records checked: {total_checked:,}")
print(f"Percentage mismatches: {total_mismatches:,}")

if total_checked > 0:
    print(
        "Overall mismatch rate: "
        f"{total_mismatches / total_checked * 100:.2f}%"
    )

print("\nREPORTS SAVED:")
print("1. change_percentage_annual_summary.csv")
print("2. change_percentage_mismatches.csv")

print("\nNo datasets were modified.")
