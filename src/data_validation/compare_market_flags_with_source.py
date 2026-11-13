
from pathlib import Path
import pandas as pd


# ============================================================
# COMPARE MARKET FLAGS WITH ORIGINAL CLEANED SOURCE RECORDS
# ============================================================
# Purpose:
# Compare suspicious standardized records with their matching
# records in data/cleaned.
#
# This is a read-only investigation.
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

CLEANED_DIR = ROOT / "data" / "cleaned"
REPORT_DIR = ROOT / "reports" / "cleaning"

FLAGS_FILE = REPORT_DIR / "market_integrity_investigation.csv"

flags = pd.read_csv(FLAGS_FILE)

# Only investigate daily-range and zero-previous flags.
flags = flags[
    flags["issue"].isin([
        "day_price_outside_daily_range",
        "zero_previous"
    ])
].copy()


def find_column(df, possible_names):
    """Find a column regardless of capitalization."""

    lookup = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for name in possible_names:
        if name.lower() in lookup:
            return lookup[name.lower()]

    raise ValueError(
        f"Could not find any of these columns: {possible_names}"
    )


print("=" * 75)
print("COMPARING FLAGS WITH ORIGINAL CLEANED SOURCE RECORDS")
print("=" * 75)

comparison_results = []

for _, flag in flags.iterrows():

    year = int(flag["source_year"])
    date = pd.to_datetime(flag["date"])

    file_path = CLEANED_DIR / f"{year}_cleaned.csv"

    source = pd.read_csv(file_path)

    date_col = find_column(source, ["DATE", "Date"])
    code_col = find_column(source, ["CODE", "Code"])

    source_dates = pd.to_datetime(
        source[date_col],
        format="mixed",
        dayfirst=True,
        errors="coerce"
    )

    source_codes = source[code_col].astype(str).str.strip()

    matches = source[
        (source_dates == date)
        & (source_codes == str(flag["code"]).strip())
    ].copy()

    print("\n" + "-" * 75)
    print(
        f"{year} | {date.date()} | "
        f"{flag['code']} | {flag['name']}"
    )
    print(f"Flag type: {flag['issue']}")
    print(f"Matching source records: {len(matches)}")

    if matches.empty:
        print("No matching source record found.")
        continue

    for column in matches.columns:
        print(f"\n{column}:")
        print(matches[column].to_string(index=False))

    for _, source_row in matches.iterrows():

        result = {
            "year": year,
            "date": date.date(),
            "code": flag["code"],
            "name": flag["name"],
            "issue": flag["issue"],
        }

        for column in matches.columns:
            result[f"source_{column}"] = source_row[column]

        comparison_results.append(result)


# ------------------------------------------------------------
# SAVE COMPARISON REPORT
# ------------------------------------------------------------

output = pd.DataFrame(comparison_results)

output_path = (
    REPORT_DIR / "market_integrity_source_comparison.csv"
)

output.to_csv(output_path, index=False)

print("\n" + "=" * 75)
print("SOURCE COMPARISON COMPLETE")
print("=" * 75)

print(f"Flags investigated: {len(flags)}")
print(f"Matching source records: {len(output)}")
print(f"Report saved: {output_path}")

print("\nNo datasets were modified.")
