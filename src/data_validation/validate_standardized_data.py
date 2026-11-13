
from pathlib import Path
import pandas as pd

# ============================================================
# 1. PROJECT PATHS AND SETTINGS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORT_DIR = PROJECT_ROOT / "reports" / "cleaning"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

YEARS = range(2007, 2026)

EXPECTED_COLUMNS = [
    "date", "code", "name",
    "12m_low", "12m_high",
    "day_low", "day_high",
    "day_price", "previous",
    "change", "change_pct",
    "volume", "adjusted_price"
]

NUMERIC_COLUMNS = [
    "12m_low", "12m_high",
    "day_low", "day_high",
    "day_price", "previous",
    "change", "change_pct",
    "volume", "adjusted_price"
]

# ============================================================
# 2. HELPER FUNCTIONS
# ============================================================

def normalize_column_name(column):
    return str(column).strip().lower()


def find_source_column(columns, standard_column):
    aliases = {
        "12m_low": ["12m low"],
        "12m_high": ["12m high"],
        "day_low": ["day low"],
        "day_high": ["day high"],
        "day_price": ["day price"],
        "previous": ["previous"],
        "change": ["change"],
        "change_pct": ["change%", "change %"],
        "volume": ["volume"],
        "adjusted_price": [
            "adjust", "adjusted", "adjusted price"
        ]
    }

    candidates = aliases.get(
        standard_column,
        [standard_column]
    )

    normalized = {
        normalize_column_name(column): column
        for column in columns
    }

    for candidate in candidates:
        if candidate in normalized:
            return normalized[candidate]

    return None


def parse_original_numeric(series):
    values = series.astype("string").str.strip()

    values = values.replace({
        "": pd.NA,
        "-": pd.NA,
        "--": pd.NA,
        "N/A": pd.NA,
        "NA": pd.NA,
        "null": pd.NA,
        "None": pd.NA
    })

    values = values.str.replace(",", "", regex=False)

    return pd.to_numeric(values, errors="coerce")


# ============================================================
# 3. REPORT COLLECTIONS
# ============================================================

summary_results = []
numeric_results = []
dtype_results = []
conversion_results = []
schema_errors = []

print("=" * 75)
print("VALIDATING STANDARDIZED NSE DATA")
print("=" * 75)

# ============================================================
# 4. PROCESS ALL YEARS
# ============================================================

for year in YEARS:

    processed_path = (
        PROCESSED_DIR / f"{year}_standardized.csv"
    )

    cleaned_path = (
        CLEANED_DIR / f"{year}_cleaned.csv"
    )

    if not processed_path.exists():
        print(f"\nWARNING: Missing {processed_path.name}")
        continue

    if not cleaned_path.exists():
        print(f"\nWARNING: Missing {cleaned_path.name}")
        continue

    df = pd.read_csv(processed_path)
    original = pd.read_csv(cleaned_path, dtype="string")

    print(f"\nYEAR: {year}")

    # --------------------------------------------------------
    # A. RECORD COUNT
    # --------------------------------------------------------

    record_count = len(df)

    count_match = len(df) == len(original)

    # --------------------------------------------------------
    # B. COLUMN VALIDATION
    # --------------------------------------------------------

    actual_columns = list(df.columns)

    missing_columns = [
        column for column in EXPECTED_COLUMNS
        if column not in actual_columns
    ]

    extra_columns = [
        column for column in actual_columns
        if column not in EXPECTED_COLUMNS
    ]

    order_match = actual_columns == EXPECTED_COLUMNS

    if missing_columns or extra_columns or not order_match:
        schema_errors.append({
            "year": year,
            "missing_columns": ", ".join(missing_columns),
            "extra_columns": ", ".join(extra_columns),
            "column_order_correct": order_match
        })

    # --------------------------------------------------------
    # C. DATA TYPE VALIDATION
    # --------------------------------------------------------

    numeric_dtype_errors = []

    for column in NUMERIC_COLUMNS:

        is_numeric = pd.api.types.is_numeric_dtype(
            df[column]
        )

        if not is_numeric:
            numeric_dtype_errors.append(column)

        dtype_results.append({
            "year": year,
            "column": column,
            "data_type": str(df[column].dtype),
            "is_numeric": is_numeric
        })

    # --------------------------------------------------------
    # D. NUMERIC VALUE ANALYSIS
    # --------------------------------------------------------

    for column in NUMERIC_COLUMNS:

        values = df[column]

        missing_count = int(values.isna().sum())

        numeric_results.append({
            "year": year,
            "column": column,
            "data_type": str(values.dtype),
            "total_records": record_count,
            "missing_count": missing_count,
            "missing_percentage": round(
                missing_count / record_count * 100, 2
            ) if record_count else 0,
            "minimum": values.min(),
            "maximum": values.max(),
            "negative_values": int((values < 0).sum())
        })

    # --------------------------------------------------------
    # E. COMPARE SOURCE AND STANDARDIZED MISSING VALUES
    # --------------------------------------------------------

    conversion_errors = []

    for column in NUMERIC_COLUMNS:

        source_column = find_source_column(
            original.columns,
            column
        )

        if source_column is None:
            conversion_results.append({
                "year": year,
                "column": column,
                "source_column": None,
                "source_missing": None,
                "standardized_missing": int(
                    df[column].isna().sum()
                ),
                "new_missing_values": None,
                "status": "SOURCE COLUMN NOT FOUND"
            })
            continue

        source_values = parse_original_numeric(
            original[source_column]
        )

        standardized_missing = df[column].isna()

        source_missing = source_values.isna()

        # Count records that were valid numeric source values
        # but became missing in the standardized dataset.
        new_missing_mask = (
            ~source_missing & standardized_missing
        )

        new_missing_count = int(new_missing_mask.sum())

        status = (
            "PASS"
            if new_missing_count == 0
            else "CHECK CONVERSION"
        )

        if new_missing_count > 0:
            conversion_errors.append(column)

        conversion_results.append({
            "year": year,
            "column": column,
            "source_column": source_column,
            "source_missing": int(source_missing.sum()),
            "standardized_missing": int(
                standardized_missing.sum()
            ),
            "new_missing_values": new_missing_count,
            "status": status
        })

    # --------------------------------------------------------
    # F. YEAR SUMMARY
    # --------------------------------------------------------

    date_values = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    summary_results.append({
        "year": year,
        "records": record_count,
        "source_records": len(original),
        "record_count_match": count_match,
        "missing_dates": int(df["date"].isna().sum()),
        "missing_codes": int(df["code"].isna().sum()),
        "missing_names": int(df["name"].isna().sum()),
        "numeric_dtype_errors": len(numeric_dtype_errors),
        "conversion_errors": len(conversion_errors),
        "column_schema_correct": (
            not missing_columns
            and not extra_columns
            and order_match
        ),
        "earliest_date": (
            date_values.min().strftime("%Y-%m-%d")
            if date_values.notna().any() else None
        ),
        "latest_date": (
            date_values.max().strftime("%Y-%m-%d")
            if date_values.notna().any() else None
        )
    })

    print(f"Records: {record_count:,}")
    print(f"Record count matches source: {count_match}")
    print(f"Column order correct: {order_match}")
    print(f"Numeric dtype errors: {len(numeric_dtype_errors)}")
    print(f"Unexpected numeric conversion errors: {len(conversion_errors)}")

# ============================================================
# 5. SAVE REPORTS
# ============================================================

summary_df = pd.DataFrame(summary_results)
numeric_df = pd.DataFrame(numeric_results)
dtype_df = pd.DataFrame(dtype_results)
conversion_df = pd.DataFrame(conversion_results)
schema_df = pd.DataFrame(schema_errors)

summary_df.to_csv(
    REPORT_DIR / "standardized_validation_summary.csv",
    index=False
)

numeric_df.to_csv(
    REPORT_DIR / "standardized_numeric_analysis.csv",
    index=False
)

dtype_df.to_csv(
    REPORT_DIR / "standardized_dtype_validation.csv",
    index=False
)

conversion_df.to_csv(
    REPORT_DIR / "standardized_conversion_comparison.csv",
    index=False
)

schema_df.to_csv(
    REPORT_DIR / "standardized_schema_errors.csv",
    index=False
)

# ============================================================
# 6. FINAL VALIDATION RESULTS
# ============================================================

print("\n" + "=" * 75)
print("STANDARDIZED DATA VALIDATION COMPLETED")
print("=" * 75)

if not summary_df.empty:

    print(f"Files processed: {len(summary_df)}")
    print(
        f"Total records: {summary_df['records'].sum():,}"
    )

    print(
        "Record count mismatches: "
        f"{(~summary_df['record_count_match']).sum()}"
    )

    print(
        "Files with incorrect schema: "
        f"{(~summary_df['column_schema_correct']).sum()}"
    )

    print(
        "Files with numeric dtype errors: "
        f"{(summary_df['numeric_dtype_errors'] > 0).sum()}"
    )

    print(
        "Files with unexpected conversion errors: "
        f"{(summary_df['conversion_errors'] > 0).sum()}"
    )

print("\nREPORTS SAVED:")
print("1. standardized_validation_summary.csv")
print("2. standardized_numeric_analysis.csv")
print("3. standardized_dtype_validation.csv")
print("4. standardized_conversion_comparison.csv")
print("5. standardized_schema_errors.csv")

print("\nNo datasets were modified.")
