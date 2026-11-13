
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_FOLDER = PROJECT_ROOT / "data" / "raw"

years_to_check = ["2007", "2008", "2009", "2017"]

for year in years_to_check:

    file_path = next(RAW_FOLDER.glob(f"*{year}.csv"))

    df = pd.read_csv(
        file_path,
        dtype=str,
        encoding="utf-8-sig"
    )

    date_column = next(
        col for col in df.columns
        if col.strip().lower() == "date"
    )

    dates = df[date_column].astype("string").str.strip()

    # Test the original inspection approach
    original_parse = pd.to_datetime(
        dates,
        errors="coerce",
        dayfirst=True
    )

    # Test mixed-format parsing
    mixed_parse = pd.to_datetime(
        dates,
        errors="coerce",
        dayfirst=True,
        format="mixed"
    )

    print("\n" + "=" * 70)
    print(f"YEAR: {year}")
    print("=" * 70)

    print("Total rows:", len(df))
    print("Unique original date strings:", dates.nunique())
    print("Missing original date strings:", dates.isna().sum())

    print("\nOriginal parsing:")
    print("Valid:", original_parse.notna().sum())
    print("Invalid:", original_parse.isna().sum())

    print("\nMixed-format parsing:")
    print("Valid:", mixed_parse.notna().sum())
    print("Invalid:", mixed_parse.isna().sum())

    print("\nFirst 20 original date values:")
    print(dates.head(20).to_list())

    print("\nExamples of values rejected by mixed parsing:")
    print(dates[mixed_parse.isna()].head(15).to_list())

    print("\nEarliest and latest mixed-parsed dates:")
    print(mixed_parse.min(), "to", mixed_parse.max())

    if year == "2017":

        print("\n2017 records with dates before 2017:")

        parsed = mixed_parse

        print(
            df.loc[
                parsed.notna() & (parsed.dt.year < 2017),
                [date_column, "CODE", "NAME"]
            ].head(20).to_string(index=False)
        )
