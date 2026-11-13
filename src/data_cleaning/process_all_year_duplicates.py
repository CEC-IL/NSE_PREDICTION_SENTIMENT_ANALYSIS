
from pathlib import Path
import pandas as pd

# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FOLDER = PROJECT_ROOT / "data" / "raw"
CLEANED_FOLDER = PROJECT_ROOT / "data" / "cleaned"
REPORT_FOLDER = PROJECT_ROOT / "reports" / "cleaning"

CLEANED_FOLDER.mkdir(parents=True, exist_ok=True)
REPORT_FOLDER.mkdir(parents=True, exist_ok=True)

YEARS = range(2007, 2026)

# ============================================================
# 2. REPORT COLLECTIONS
# ============================================================

yearly_results = []
duplicate_details = []
repeated_date_code_details = []

# ============================================================
# 3. PROCESS EACH YEAR
# ============================================================

print("=" * 75)
print("ALL-YEAR NSE EXACT DUPLICATE PROCESSING")
print("=" * 75)

for year in YEARS:

    file_path = RAW_FOLDER / f"NSE_data_all_stocks_{year}.csv"

    if not file_path.exists():
        print(f"\nWARNING: {year} file not found. Skipping.")
        continue

    print(f"\nProcessing {year}...")

    # Read original data as text to preserve original values.
    df = pd.read_csv(file_path, dtype=str)

    original_columns = list(df.columns)

    original_count = len(df)

    # Keep original CSV row numbers for audit purposes.
    df["_original_csv_row"] = range(2, original_count + 2)

    # --------------------------------------------------------
    # 4. IDENTIFY 2017 ANOMALIES
    # --------------------------------------------------------

    anomaly_mask = pd.Series(False, index=df.index)

    date_column = next(
        (
            column for column in original_columns
            if column.strip().lower() == "date"
        ),
        None
    )

    if year == 2017:

        if date_column is None:
            raise ValueError("2017 file has no date column.")

        parsed_dates = pd.to_datetime(
            df[date_column].astype("string").str.strip(),
            format="%d-%b-%y",
            errors="coerce"
        )

        anomaly_mask = (
            parsed_dates < pd.Timestamp("2017-01-01")
        )

        if anomaly_mask.sum() != 70:
            raise ValueError(
                f"Expected 70 anomalies in 2017, "
                f"found {anomaly_mask.sum()}. Stopping."
            )

    excluded_anomalies = df.loc[anomaly_mask].copy()

    # Analytical records exclude the known 2017 anomaly block.
    analytical = df.loc[~anomaly_mask].copy()

    # --------------------------------------------------------
    # 5. IDENTIFY EXACT DUPLICATES
    # --------------------------------------------------------

    # Count duplicate rows in the original raw file.
    raw_duplicate_mask = df.duplicated(
        subset=original_columns,
        keep="first"
    )

    raw_exact_duplicates = int(raw_duplicate_mask.sum())

    # Identify exact duplicates among analytical records.
    duplicate_mask = analytical.duplicated(
        subset=original_columns,
        keep="first"
    )

    duplicates_to_remove = analytical.loc[duplicate_mask].copy()

    # Save details of exact duplicate rows removed.
    for _, row in duplicates_to_remove.iterrows():

        duplicate_details.append({
            "year": year,
            "original_csv_row": row["_original_csv_row"],
            "date": row[date_column] if date_column else None,
            "code": next(
                (
                    row[column]
                    for column in original_columns
                    if column.strip().lower() == "code"
                ),
                None
            ),
            "name": next(
                (
                    row[column]
                    for column in original_columns
                    if column.strip().lower() == "name"
                ),
                None
            ),
        })

    # Remove only exact duplicates.
    cleaned = analytical.loc[~duplicate_mask].copy()

    # --------------------------------------------------------
    # 6. IDENTIFY REPEATED DATE + STOCK CODE
    # --------------------------------------------------------

    code_column = next(
        (
            column for column in original_columns
            if column.strip().lower() == "code"
        ),
        None
    )

    repeated_groups = 0
    repeated_records = 0

    if date_column and code_column:

        valid_keys = cleaned[
            cleaned[date_column].notna()
            & cleaned[code_column].notna()
        ]

        group_sizes = (
            valid_keys.groupby(
                [date_column, code_column],
                dropna=False
            )
            .size()
            .reset_index(name="record_count")
        )

        repeated_groups_df = group_sizes[
            group_sizes["record_count"] > 1
        ].copy()

        repeated_groups = len(repeated_groups_df)

        repeated_records = int(
            repeated_groups_df["record_count"].sum()
        )

        for _, group in repeated_groups_df.iterrows():

            repeated_date_code_details.append({
                "year": year,
                "date": group[date_column],
                "code": group[code_column],
                "record_count": group["record_count"],
            })

    # --------------------------------------------------------
    # 7. SAVE CLEANED ANNUAL DATA
    # --------------------------------------------------------

    cleaned = cleaned.drop(columns=["_original_csv_row"])

    output_file = (
        CLEANED_FOLDER / f"{year}_cleaned.csv"
    )

    cleaned.to_csv(output_file, index=False)

    # --------------------------------------------------------
    # 8. VERIFY OUTPUT
    # --------------------------------------------------------

    saved = pd.read_csv(output_file, dtype=str)

    if len(saved) != len(cleaned):
        raise ValueError(f"{year}: saved row count mismatch.")

    if saved.duplicated(subset=original_columns).any():
        raise ValueError(
            f"{year}: exact duplicates remain in output."
        )

    if len(df) != (
        len(cleaned)
        + len(duplicates_to_remove)
        + len(excluded_anomalies)
    ):
        raise ValueError(
            f"{year}: record count reconciliation failed."
        )

    # --------------------------------------------------------
    # 9. YEARLY SUMMARY
    # --------------------------------------------------------

    yearly_results.append({
        "year": year,
        "original_records": original_count,
        "raw_exact_duplicates": raw_exact_duplicates,
        "anomalies_excluded": len(excluded_anomalies),
        "exact_duplicates_removed": len(duplicates_to_remove),
        "cleaned_records": len(cleaned),
        "repeated_date_code_groups": repeated_groups,
        "records_in_repeated_groups": repeated_records,
    })

    print(f"  Original records: {original_count:,}")
    print(f"  Exact duplicates in raw file: {raw_exact_duplicates:,}")
    print(f"  2017 anomalies excluded: {len(excluded_anomalies):,}")
    print(f"  Exact duplicates removed: {len(duplicates_to_remove):,}")
    print(f"  Repeated date/code groups retained: {repeated_groups:,}")
    print(f"  Cleaned records: {len(cleaned):,}")

# ============================================================
# 10. SAVE COMBINED REPORTS
# ============================================================

yearly_report = pd.DataFrame(yearly_results)

duplicate_report = pd.DataFrame(
    duplicate_details,
    columns=[
        "year",
        "original_csv_row",
        "date",
        "code",
        "name",
    ]
)

repeated_report = pd.DataFrame(
    repeated_date_code_details,
    columns=[
        "year",
        "date",
        "code",
        "record_count",
    ]
)

yearly_report.to_csv(
    REPORT_FOLDER / "all_years_duplicate_summary.csv",
    index=False
)

duplicate_report.to_csv(
    REPORT_FOLDER / "all_years_exact_duplicates_removed.csv",
    index=False
)

repeated_report.to_csv(
    REPORT_FOLDER / "all_years_repeated_date_code.csv",
    index=False
)

# ============================================================
# 11. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 75)
print("ALL-YEAR PROCESSING COMPLETED")
print("=" * 75)

print("\nYEARLY RESULTS:")
print(yearly_report.to_string(index=False))

print("\nTOTALS:")
print(f"Original records: {yearly_report['original_records'].sum():,}")
print(f"Exact duplicates removed: {yearly_report['exact_duplicates_removed'].sum():,}")
print(f"2017 anomalies excluded: {yearly_report['anomalies_excluded'].sum():,}")
print(f"Cleaned records: {yearly_report['cleaned_records'].sum():,}")
print(f"Repeated date/code groups retained: {yearly_report['repeated_date_code_groups'].sum():,}")

print("\nREPORTS SAVED:")
print(REPORT_FOLDER / "all_years_duplicate_summary.csv")
print(REPORT_FOLDER / "all_years_exact_duplicates_removed.csv")
print(REPORT_FOLDER / "all_years_repeated_date_code.csv")

print("\nOriginal raw CSV files were not modified.")
