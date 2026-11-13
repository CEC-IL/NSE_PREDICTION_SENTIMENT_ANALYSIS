
from pathlib import Path
import pandas as pd

#PATHS
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_FOLDER = PROJECT_ROOT / "data" / "raw"
REPORT_FOLDER = PROJECT_ROOT / "reports" / "cleaning"
REPORT_FOLDER.mkdir(parents=True, exist_ok=True)


def read_csv_file(file_path):
    encodings = ["utf-8-sig", "cp1252", "latin1"]
    for encoding in encodings:
        try:
            df = pd.read_csv(
                file_path,
                encoding=encoding,
                low_memory=False
            )
            return df
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not read file: {file_path.name}")


# --------------------------------------------------
# 3. INSPECT INDIVIDUAL FILES
# --------------------------------------------------

inventory = []
column_profiles = []

csv_files = sorted(RAW_FOLDER.glob("*.csv"))

print("=" * 75)
print("NSE RAW HISTORICAL DATA INSPECTION")
print("=" * 75)

print(f"\nFiles found: {len(csv_files)}")

for file_path in csv_files:

    print("\n" + "-" * 75)
    print(f"FILE: {file_path.name}")

    df = read_csv_file(file_path)

    rows, columns = df.shape

    # Identify possible date columns
    date_columns = [
        col for col in df.columns
        if "date" in str(col).lower()
    ]

    date_column = date_columns[0] if date_columns else None

    date_min = None
    date_max = None
    valid_dates = 0

    if date_column:

        parsed_dates = pd.to_datetime(
            df[date_column],
            errors="coerce",
            dayfirst=True
        )

        valid_dates = int(parsed_dates.notna().sum())

        if valid_dates > 0:
            date_min = parsed_dates.min()
            date_max = parsed_dates.max()

    # Exact duplicate rows
    duplicate_rows = int(df.duplicated().sum())

    # Overall missing values
    total_missing = int(df.isna().sum().sum())

    print(f"Rows: {rows:,}")
    print(f"Columns: {columns}")
    print(f"Exact duplicate rows: {duplicate_rows:,}")
    print(f"Missing values: {total_missing:,}")

    print("\nCOLUMN NAMES:")
    print(list(df.columns))

    if date_column:
        print(f"\nDate column: {date_column}")
        print(f"Valid dates: {valid_dates:,}")
        print(f"Date range: {date_min} to {date_max}")
    else:
        print("\nNo date column identified.")

    # Store file-level summary
    inventory.append({
        "file_name": file_path.name,
        "rows": rows,
        "columns": columns,
        "date_column": date_column,
        "valid_dates": valid_dates,
        "date_min": date_min,
        "date_max": date_max,
        "exact_duplicate_rows": duplicate_rows,
        "total_missing_values": total_missing,
        "column_names": " | ".join(map(str, df.columns))
    })

    # Store column-level summary
    for column in df.columns:

        series = df[column]

        column_profiles.append({
            "file_name": file_path.name,
            "column_name": str(column),
            "data_type": str(series.dtype),
            "missing_values": int(series.isna().sum()),
            "dash_placeholders": int(
                series.astype("string").str.strip().eq("-").sum()
            ),
            "unique_values": int(series.nunique(dropna=True))
        })


# --------------------------------------------------
# 4. SAVE REPORTS
# --------------------------------------------------

inventory_df = pd.DataFrame(inventory)
profiles_df = pd.DataFrame(column_profiles)

inventory_path = REPORT_FOLDER / "raw_data_inventory.csv"
profiles_path = REPORT_FOLDER / "raw_column_profiles.csv"

inventory_df.to_csv(inventory_path, index=False)
profiles_df.to_csv(profiles_path, index=False)


# --------------------------------------------------
# 5. FINAL SUMMARY
# --------------------------------------------------

print("\n" + "=" * 75)
print("INSPECTION COMPLETED")
print("=" * 75)

print(f"Files inspected: {len(csv_files)}")

if not inventory_df.empty:

    print(f"Total rows across files: {inventory_df['rows'].sum():,}")

    print(
        "Total exact duplicate rows across files: "
        f"{inventory_df['exact_duplicate_rows'].sum():,}"
    )

    print(
        "Total missing values across files: "
        f"{inventory_df['total_missing_values'].sum():,}"
    )

print("\nREPORTS CREATED:")
print(inventory_path)
print(profiles_path)

print("\nNo original CSV files were modified.")
