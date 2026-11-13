
from pathlib import Path
import pandas as pd

# ============================================================
# 1. PROJECT PATHS AND SETTINGS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = PROJECT_ROOT / "data" / "cleaned"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
REPORT_DIR = PROJECT_ROOT / "reports" / "cleaning"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

YEARS = range(2007, 2026)

STANDARD_COLUMNS = [
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
    "adjusted_price"
]

COLUMN_ALIASES = {
    "date": ["date"],
    "code": ["code"],
    "name": ["name"],
    "12m_low": ["12m low"],
    "12m_high": ["12m high"],
    "day_low": ["day low"],
    "day_high": ["day high"],
    "day_price": ["day price"],
    "previous": ["previous"],
    "change": ["change"],
    "change_pct": ["change%", "change %"],
    "volume": ["volume"],
    "adjusted_price": ["adjust", "adjusted", "adjusted price"]
}

NUMERIC_COLUMNS = [
    "12m_low",
    "12m_high",
    "day_low",
    "day_high",
    "day_price",
    "previous",
    "change",
    "change_pct",
    "volume",
    "adjusted_price"
]

# ============================================================
# 2. HELPER FUNCTIONS
# ============================================================

def normalize_column_name(column):
    return str(column).strip().lower()


def find_column_mapping(columns):
    mapping = {}

    normalized_columns = {
        normalize_column_name(column): column
        for column in columns
    }

    for standard_name, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in normalized_columns:
                mapping[standard_name] = normalized_columns[alias]
                break

    return mapping


def clean_numeric_column(series):
    values = series.astype("string").str.strip()

    # Treat common source placeholders as missing.
    values = values.replace({
        "": pd.NA,
        "-": pd.NA,
        "--": pd.NA,
        "N/A": pd.NA,
        "NA": pd.NA,
        "null": pd.NA,
        "None": pd.NA
    })

    # Remove thousands separators.
    values = values.str.replace(",", "", regex=False)

    return pd.to_numeric(values, errors="coerce")


# ============================================================
# 3. PROCESS ALL ANNUAL FILES
# ============================================================

summary_results = []
missing_results = []
mapping_results = []

print("=" * 75)
print("STANDARDIZING NSE HISTORICAL DATA")
print("=" * 75)

for year in YEARS:

    input_path = INPUT_DIR / f"{year}_cleaned.csv"
    output_path = OUTPUT_DIR / f"{year}_standardized.csv"

    if not input_path.exists():
        print(f"\nWARNING: Missing file: {input_path.name}")
        continue

    df = pd.read_csv(input_path, dtype="string")

    original_count = len(df)

    mapping = find_column_mapping(df.columns)

    missing_columns = [
        column for column in STANDARD_COLUMNS
        if column not in mapping
    ]

    if missing_columns:
        raise ValueError(
            f"{year}: Missing required columns: {missing_columns}"
        )

    standardized = pd.DataFrame(index=df.index)

    # --------------------------------------------------------
    # MAP SOURCE COLUMNS TO STANDARD COLUMN NAMES
    # --------------------------------------------------------

    for standard_name in STANDARD_COLUMNS:
        source_name = mapping[standard_name]
        standardized[standard_name] = df[source_name]

        mapping_results.append({
            "year": year,
            "standard_column": standard_name,
            "source_column": source_name
        })

    # --------------------------------------------------------
    # CLEAN TEXT COLUMNS
    # --------------------------------------------------------

    for column in ["code", "name"]:
        standardized[column] = (
            standardized[column]
            .astype("string")
            .str.strip()
        )

        standardized[column] = standardized[column].replace({
            "": pd.NA,
            "-": pd.NA
        })

    # --------------------------------------------------------
    # STANDARDIZE DATES
    # --------------------------------------------------------

    standardized["date"] = pd.to_datetime(
        standardized["date"],
        format="mixed",
        dayfirst=True,
        errors="coerce"
    )

    standardized["date"] = standardized["date"].dt.strftime(
        "%Y-%m-%d"
    )

    # --------------------------------------------------------
    # CONVERT NUMERIC COLUMNS
    # --------------------------------------------------------

    for column in NUMERIC_COLUMNS:
        standardized[column] = clean_numeric_column(
            standardized[column]
        )

    # --------------------------------------------------------
    # VERIFY RECORD COUNT
    # --------------------------------------------------------

    if len(standardized) != original_count:
        raise RuntimeError(
            f"{year}: Record count changed during standardization."
        )

    # --------------------------------------------------------
    # SAVE STANDARDIZED DATASET
    # --------------------------------------------------------

    standardized.to_csv(output_path, index=False)

    # --------------------------------------------------------
    # VERIFY SAVED OUTPUT
    # --------------------------------------------------------

    verification = pd.read_csv(output_path)

    if len(verification) != original_count:
        raise RuntimeError(
            f"{year}: Saved record count verification failed."
        )

    if list(verification.columns) != STANDARD_COLUMNS:
        raise RuntimeError(
            f"{year}: Column order verification failed."
        )

    # --------------------------------------------------------
    # RECORD MISSING VALUES
    # --------------------------------------------------------

    for column in STANDARD_COLUMNS:
        missing_count = int(standardized[column].isna().sum())

        missing_results.append({
            "year": year,
            "column": column,
            "missing_count": missing_count,
            "missing_percentage": round(
                missing_count / original_count * 100, 2
            ) if original_count else 0
        })

    summary_results.append({
        "year": year,
        "records_before": original_count,
        "records_after": len(standardized),
        "date_missing": int(standardized["date"].isna().sum()),
        "code_missing": int(standardized["code"].isna().sum()),
        "name_missing": int(standardized["name"].isna().sum())
    })

    print(f"\nYEAR: {year}")
    print(f"Records before: {original_count:,}")
    print(f"Records after: {len(standardized):,}")
    print(f"Missing dates: {standardized['date'].isna().sum():,}")
    print(f"Missing stock codes: {standardized['code'].isna().sum():,}")
    print(f"Missing stock names: {standardized['name'].isna().sum():,}")
    print(f"Saved: {output_path.name}")

# ============================================================
# 4. SAVE STANDARDIZATION REPORTS
# ============================================================

summary_df = pd.DataFrame(summary_results)
missing_df = pd.DataFrame(missing_results)
mapping_df = pd.DataFrame(mapping_results)

summary_df.to_csv(
    REPORT_DIR / "standardization_summary.csv",
    index=False
)

missing_df.to_csv(
    REPORT_DIR / "standardization_missing_values.csv",
    index=False
)

mapping_df.to_csv(
    REPORT_DIR / "standardization_column_mapping.csv",
    index=False
)

# ============================================================
# 5. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 75)
print("STANDARDIZATION COMPLETED")
print("=" * 75)

if not summary_df.empty:
    print(f"Files processed: {len(summary_df)}")
    print(f"Total records: {summary_df['records_after'].sum():,}")
    print(
        "Missing dates across all files: "
        f"{summary_df['date_missing'].sum():,}"
    )

print("\nSTANDARDIZED FILES:")
print(OUTPUT_DIR)

print("\nREPORTS SAVED:")
print("1. standardization_summary.csv")
print("2. standardization_missing_values.csv")
print("3. standardization_column_mapping.csv")

print("\nOriginal raw and cleaned datasets were not modified.")
