
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

# ============================================================
# 2. HELPER FUNCTION: FIND DATE COLUMN
# ============================================================

def find_date_column(df):
    for column in df.columns:
        if column.strip().lower() == "date":
            return column
    return None


# ============================================================
# 3. HELPER FUNCTION: IDENTIFY COMMON DATE FORMATS
# ============================================================

def identify_date_format(value):
    if pd.isna(value):
        return "MISSING"

    value = str(value).strip()

    formats = [
        ("%d-%b-%y", "DD-MMM-YY"),
        ("%d-%b-%Y", "DD-MMM-YYYY"),
        ("%Y-%m-%d", "YYYY-MM-DD"),
        ("%d/%m/%Y", "DD/MM/YYYY"),
        ("%m/%d/%Y", "MM/DD/YYYY"),
        ("%d/%m/%y", "DD/MM/YY"),
        ("%m/%d/%y", "MM/DD/YY"),
    ]

    for date_format, label in formats:
        try:
            pd.to_datetime(value, format=date_format, errors="raise")
            return label
        except (ValueError, TypeError):
            continue

    return "UNRECOGNIZED"


# ============================================================
# 4. PROCESS ALL CLEANED FILES
# ============================================================

summary_results = []
format_results = []
invalid_date_results = []
outside_year_results = []

print("=" * 75)
print("ALL-YEAR DATE VALIDATION")
print("=" * 75)

for year in YEARS:

    file_path = CLEANED_DIR / f"{year}_cleaned.csv"

    if not file_path.exists():
        print(f"\nWARNING: Missing file: {file_path.name}")
        continue

    df = pd.read_csv(file_path)

    date_column = find_date_column(df)

    if date_column is None:
        print(f"\nERROR: No date column found in {file_path.name}")
        continue

    raw_dates = df[date_column]

    # Parse dates using flexible diagnostic parsing.
    parsed_dates = pd.to_datetime(
        raw_dates,
        format="mixed",
        dayfirst=True,
        errors="coerce"
    )

    missing_dates = raw_dates.isna() | raw_dates.astype(str).str.strip().eq("")
    invalid_dates = parsed_dates.isna() & ~missing_dates

    outside_year = (
        parsed_dates.notna()
        & (parsed_dates.dt.year != year)
    )

    valid_dates = parsed_dates.notna()

    earliest_date = (
        parsed_dates[valid_dates].min()
        if valid_dates.any()
        else None
    )

    latest_date = (
        parsed_dates[valid_dates].max()
        if valid_dates.any()
        else None
    )

    # --------------------------------------------------------
    # FORMAT DISTRIBUTION
    # --------------------------------------------------------

    formats = raw_dates.apply(identify_date_format)

    format_counts = formats.value_counts(dropna=False)

    for format_name, count in format_counts.items():
        format_results.append({
            "year_file": year,
            "date_format": format_name,
            "record_count": count
        })

    # --------------------------------------------------------
    # INVALID DATE DETAILS
    # --------------------------------------------------------

    for index in df.index[invalid_dates]:
        invalid_date_results.append({
            "year_file": year,
            "csv_row_number": index + 2,
            "raw_date": raw_dates.loc[index]
        })

    # --------------------------------------------------------
    # DATES OUTSIDE EXPECTED YEAR
    # --------------------------------------------------------

    for index in df.index[outside_year]:
        outside_year_results.append({
            "year_file": year,
            "csv_row_number": index + 2,
            "raw_date": raw_dates.loc[index],
            "parsed_date": parsed_dates.loc[index].strftime("%Y-%m-%d"),
            "actual_year": parsed_dates.loc[index].year
        })

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    summary_results.append({
        "year_file": year,
        "total_records": len(df),
        "valid_dates": int(valid_dates.sum()),
        "missing_dates": int(missing_dates.sum()),
        "invalid_dates": int(invalid_dates.sum()),
        "dates_outside_expected_year": int(outside_year.sum()),
        "earliest_date": (
            earliest_date.strftime("%Y-%m-%d")
            if earliest_date is not None else None
        ),
        "latest_date": (
            latest_date.strftime("%Y-%m-%d")
            if latest_date is not None else None
        )
    })

    print(f"\nYEAR: {year}")
    print(f"Total records: {len(df):,}")
    print(f"Valid dates: {valid_dates.sum():,}")
    print(f"Missing dates: {missing_dates.sum():,}")
    print(f"Invalid dates: {invalid_dates.sum():,}")
    print(f"Dates outside expected year: {outside_year.sum():,}")
    print(f"Earliest date: {earliest_date}")
    print(f"Latest date: {latest_date}")

# ============================================================
# 5. SAVE REPORTS
# ============================================================

summary_df = pd.DataFrame(summary_results)
formats_df = pd.DataFrame(format_results)
invalid_df = pd.DataFrame(invalid_date_results)
outside_year_df = pd.DataFrame(outside_year_results)

summary_df.to_csv(
    REPORT_DIR / "all_years_date_summary.csv",
    index=False
)

formats_df.to_csv(
    REPORT_DIR / "all_years_date_formats.csv",
    index=False
)

invalid_df.to_csv(
    REPORT_DIR / "all_years_invalid_dates.csv",
    index=False
)

outside_year_df.to_csv(
    REPORT_DIR / "all_years_outside_year_dates.csv",
    index=False
)

# ============================================================
# 6. FINAL RESULTS
# ============================================================

print("\n" + "=" * 75)
print("DATE VALIDATION COMPLETED")
print("=" * 75)

print("\nTOTALS:")
if not summary_df.empty:
    print(f"Files processed: {len(summary_df)}")
    print(f"Total records: {summary_df['total_records'].sum():,}")
    print(f"Valid dates: {summary_df['valid_dates'].sum():,}")
    print(f"Missing dates: {summary_df['missing_dates'].sum():,}")
    print(f"Invalid dates: {summary_df['invalid_dates'].sum():,}")
    print(
        "Dates outside expected year: "
        f"{summary_df['dates_outside_expected_year'].sum():,}"
    )

print("\nREPORTS SAVED:")
print("1. all_years_date_summary.csv")
print("2. all_years_date_formats.csv")
print("3. all_years_invalid_dates.csv")
print("4. all_years_outside_year_dates.csv")

print("\nNo source datasets were modified.")
