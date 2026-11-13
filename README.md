# NSE Stock Market Analysis and Prediction Platform

## 1. Project Overview

The **NSE Stock Market Analysis and Prediction Platform** is a data-driven project focused on analyzing historical market data from companies listed on the Nairobi Securities Exchange (NSE).

The project aims to develop a platform that combines historical stock market data, machine learning, financial news, and sentiment analysis to provide market insights and stock price predictions.

The development process is divided into several stages, beginning with historical data preparation and validation before moving into liquidity analysis, feature engineering, machine learning, news collection, and eventually web application development.

The project uses Python for data processing and machine learning, with a planned web application to present the resulting analysis and predictions.

### Main objectives

1. Collect and organize historical NSE market data.
2. Clean and standardize historical datasets.
3. Validate data quality and identify suspicious market values.
4. Combine annual datasets into a master historical dataset.
5. Classify listed securities into liquid and illiquid groups.
6. Develop and compare stock prediction models.
7. Collect relevant financial news and NSE announcements.
8. Analyze news sentiment and its potential influence on stock performance.
9. Compare market-data-only models against news-enhanced models.
10. Develop a web-based NSE market intelligence and prediction platform.

---

## 2. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data processing and machine learning |
| Pandas | Data cleaning, transformation, validation and analysis |
| NumPy | Numerical computations in future analysis |
| Scikit-learn | Machine learning and model evaluation |
| XGBoost | Gradient-boosting prediction models |
| Statsmodels | Statistical analysis and ARIMA modelling |
| Matplotlib / Seaborn | Data visualization |
| Requests | HTTP requests for data collection |
| BeautifulSoup | Web scraping |
| Feedparser | RSS news collection |
| Next.js | Planned frontend application |
| Node.js | Planned backend services |
| Supabase | Planned database and backend infrastructure |
| Git and GitHub | Version control and project management |

**Dependency status:** Pandas is confirmed as the core library used by the completed data-processing scripts. The remaining packages represent the project technology requirements and planned development stack. Their installation status should be verified against the actual virtual environment and `requirements.txt`.

---

## 3. Development Environment

### Operating system

- Windows
- PowerShell terminal
- Visual Studio Code

### Python environment

The project uses a Python virtual environment named `.venv`.

Python 3.13 was selected as the project target, with Python 3.14 also available on the development machine.

### Environment setup

Create the virtual environment:

```powershell
py -3.13 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install project dependencies:

```powershell
python -m pip install -r requirements.txt
```

Verify the Python version:

```powershell
python --version
```

Verify installed packages:

```powershell
python -m pip list
```

Export the exact installed package versions when preparing the environment for reproducible development:

```powershell
python -m pip freeze > requirements.txt
```

The virtual environment should not be committed to GitHub. Other developers should recreate it using the dependency file.

---

## 4. Project Directory Structure

The project is organized into separate directories for historical data, processing scripts, reports, models and future application development.

```text
NSE_PREDICTION/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/
│   ├── cleaned/
│   ├── processed/
│   ├── liquid/
│   ├── illiquid/
│   └── news/
│
├── src/
│   ├── data_cleaning/
│   ├── data_validation/
│   ├── liquidity_analysis/
│   ├── feature_engineering/
│   ├── news_collector/
│   ├── modelling/
│   │   ├── baseline/
│   │   ├── xgboost/
│   │   ├── random_forest/
│   │   └── arima/
│   │
│   └── evaluation/
│
├── models/
│   ├── liquid/
│   └── illiquid/
│
├── reports/
│   ├── cleaning/
│   ├── liquidity/
│   ├── modelling/
│   └── news/
│
└── notebooks/
```

### Directory descriptions

| Directory | Responsibility |
|---|---|
| `data/raw/` | Original historical NSE CSV files |
| `data/cleaned/` | Annual datasets after duplicate handling and blank-row removal |
| `data/processed/` | Standardized annual datasets and the planned master dataset |
| `data/liquid/` | Future liquid-security datasets |
| `data/illiquid/` | Future illiquid-security datasets |
| `data/news/` | Future collected financial news |
| `src/data_cleaning/` | Scripts for cleaning and combining datasets |
| `src/data_validation/` | Data-quality and integrity validation scripts |
| `src/liquidity_analysis/` | Future liquidity classification |
| `src/feature_engineering/` | Future model feature creation |
| `src/news_collector/` | Future news collection and processing |
| `src/modelling/` | Prediction model implementations |
| `src/evaluation/` | Model evaluation and comparison |
| `models/` | Saved trained models |
| `reports/` | Generated reports and analysis results |
| `notebooks/` | Exploratory analysis and experiments |

---

## 5. Historical NSE Dataset

### Source data

The project currently uses historical NSE CSV files covering 2007–2025.

There are 19 original annual datasets:

```text
NSE_data_all_stocks_2007.csv
NSE_data_all_stocks_2008.csv
NSE_data_all_stocks_2009.csv
...
NSE_data_all_stocks_2025.csv
```

The files are stored in:

```text
data/raw/
```

The original files were copied into the new project from the previous historical-data project. The previous project files have been preserved.

### Initial dataset inventory

| Year | Original records |
|---|---:|
| 2007 | 10,608 |
| 2008 | 10,583 |
| 2009 | 14,386 |
| 2010 | 14,952 |
| 2011 | 14,931 |
| 2012 | 16,044 |
| 2013 | 14,889 |
| 2014 | 15,696 |
| 2015 | 16,386 |
| 2016 | 16,800 |
| 2017 | 16,981 |
| 2018 | 17,651 |
| 2019 | 18,147 |
| 2020 | 17,892 |
| 2021 | 17,746 |
| 2022 | 16,806 |
| 2023 | 17,274 |
| 2024 | 18,119 |
| 2025 | 15,114 |
| **Total** | **301,005** |

The 2025 dataset ends on 31 October 2025.

---

# 6. Data Cleaning and Preparation

The initial objective was to preserve the original information while producing consistent annual datasets suitable for analysis.

All cleaning operations were performed on copies of the original data.

**The original CSV files in `data/raw/` were never modified.**

## 6.1 Raw data inspection

Script:

```text
src/data_validation/inspect_raw_data.py
```

The first inspection examined:

- Annual record counts.
- Column names and variations.
- Missing values.
- Duplicate records.
- Data types.
- Placeholder values.
- Differences between annual datasets.

Generated reports:

```text
reports/cleaning/
├── raw_data_inventory.csv
└── raw_column_profiles.csv
```

The original datasets contained 13 columns, but their naming conventions varied between years.

Examples included:

- `DATE` and `Date`
- `CODE` and `Code`
- `NAME` and `Name`
- `Adjust`, `Adjusted` and `Adjusted Price`
- `Change%` and `Change %`

These differences required a standardization stage.

## 6.2 Investigation and exclusion of 2017 anomalies

During inspection, 70 records dated `09-May-15` were identified inside the 2017 dataset.

These records formed one continuous block in the original file, occupying CSV rows 6016–6085.

The investigation examined whether the records belonged to 2015 or had been copied from another historical dataset.

Findings:

- 70 anomalous records were identified.
- 67 stock codes were also found in the 2015 dataset.
- Three codes were not found in the 2015 dataset.
- Exact matching across the investigated external records did not establish that the records should be transferred to 2015.

### Decision

The 70 records were excluded from the 2017 analytical dataset.

They were not transferred to 2015, and their original dates were not changed.

The excluded records were preserved separately for auditing.

Script:

```text
src/data_cleaning/exclude_2017_anomalies.py
```

Outputs:

```text
data/cleaned/2017_after_anomaly_exclusion.csv

reports/cleaning/2017_excluded_anomalies.csv
```

The original 2017 raw file remains unchanged.

## 6.3 Duplicate handling

Duplicate processing was applied across all 19 annual datasets.

Two types of repeated records were distinguished.

**Exact duplicate records**

Rows identical across all original columns were treated as exact duplicates. Additional copies were removed.

**Repeated date and stock-code records**

Records sharing the same date and stock code were not automatically treated as duplicates.

If other fields differed, the records were retained because they may represent different market snapshots or values.

### Duplicate processing results

| Year | Exact duplicates removed | Cleaned records |
|---|---:|---:|
| 2009 | 19 | 14,367 |
| 2017 | 69 | 16,842 |
| Other years | 0 | Unchanged |
| **Total** | **88** | **300,847 before blank-row removal** |

The 2017 count also accounts for the 70 excluded anomalous records.

The 2009 dataset contained 139 repeated date/code groups, involving 278 records. These records were retained.

### Decision

- Remove only exact duplicate copies.
- Retain non-identical repeated date/code records.
- Preserve missing-value records.
- Never modify original raw files.

Script:

```text
src/data_cleaning/process_all_year_duplicates.py
```

Generated reports:

```text
reports/cleaning/
├── all_years_duplicate_summary.csv
├── all_years_exact_duplicates_removed.csv
└── all_years_repeated_date_code.csv
```

## 6.4 Date validation

Script:

```text
src/data_validation/investigate_all_year_dates.py
```

All 19 cleaned annual datasets were checked using flexible date parsing with day-first interpretation.

Results before completely blank-row removal:

| Check | Result |
|---|---:|
| Total records | 300,847 |
| Valid dates | 300,845 |
| Missing dates | 2 |
| Invalid dates | 0 |
| Dates outside expected annual file year | 0 |

The two missing dates belonged to completely blank records in 2014 and 2018.

The earlier apparent parsing issues in 2007–2012 were caused by date-parser inference rather than invalid source dates.

Reports:

```text
reports/cleaning/
├── all_years_date_summary.csv
├── all_years_date_formats.csv
├── all_years_invalid_dates.csv
└── all_years_outside_year_dates.csv
```

## 6.5 Removal of completely blank rows

Two completely blank records were identified:

- One in 2014.
- One in 2018.

These records contained no information in any column.

They were removed from the cleaned annual datasets and preserved in the audit report.

Script:

```text
src/data_cleaning/remove_fully_blank_rows.py
```

Results:

| Description | Count |
|---|---:|
| Blank rows removed | 2 |
| Final records after removal | 300,845 |
| Remaining completely blank rows | 0 |

Reports:

```text
reports/cleaning/
├── fully_blank_rows_summary.csv
└── fully_blank_rows_removed.csv
```

## 6.6 Standardization of annual datasets

The 19 annual datasets were standardized into one consistent 13-column schema.

Script:

```text
src/data_cleaning/standardize_all_years.py
```

Input:

```text
data/cleaned/
```

Output:

```text
data/processed/
```

### Standardized schema

| Column | Description |
|---|---|
| `date` | Trading date |
| `code` | NSE stock ticker |
| `name` | Company or security name |
| `12m_low` | 12-month low price |
| `12m_high` | 12-month high price |
| `day_low` | Reported daily low |
| `day_high` | Reported daily high |
| `day_price` | Reported daily price |
| `previous` | Previous price |
| `change` | Reported price change |
| `change_pct` | Reported percentage change |
| `volume` | Trading volume |
| `adjusted_price` | Adjusted price, where available |

### Standardization rules

1. Column-name variations were mapped to a common schema.
2. Dates were converted to ISO format: `YYYY-MM-DD`.
3. Stock codes and company names were trimmed.
4. Empty strings and dash placeholders were treated as missing.
5. Numeric columns were converted into numeric data types.
6. Thousands separators were removed.
7. Missing values were not replaced with zero.
8. The standardized datasets were saved separately from the cleaned datasets.

Results:

- 19 annual files processed.
- 300,845 records retained.
- 13 standardized columns.
- Zero missing dates.
- Zero missing stock codes.
- 48 missing stock names inherited from the source data.

Reports:

```text
reports/cleaning/
├── standardization_summary.csv
├── standardization_missing_values.csv
└── standardization_column_mapping.csv
```

## 6.7 Numeric conversion validation

Script:

```text
src/data_validation/validate_standardized_data.py
```

The standardized datasets were compared with the cleaned input datasets.

Checks included:

- Column schema and ordering.
- Record-count consistency.
- Numeric data types.
- Minimum and maximum values.
- Missing numeric values.
- Negative numeric values.
- Unexpected conversion losses.

Results:

| Validation | Result |
|---|---:|
| Annual files processed | 19 |
| Total records | 300,845 |
| Record-count mismatches | 0 |
| Incorrect schemas | 0 |
| Numeric data-type errors | 0 |
| Unexpected conversion errors | 0 |

All 19 annual datasets passed the conversion and schema validation checks.

Important: These checks establish that the standardization process preserved the records and converted values successfully. They do not independently establish that every market value is economically correct.

Reports:

```text
reports/cleaning/
├── standardized_validation_summary.csv
├── standardized_numeric_analysis.csv
├── standardized_dtype_validation.csv
├── standardized_conversion_comparison.csv
└── standardized_schema_errors.csv
```

---

# 7. Market-Value Integrity Investigation

After standardization, the datasets were checked for suspicious market values.

Script:

```text
src/data_validation/validate_market_value_integrity.py
```

The checks included:

1. Negative prices.
2. Zero prices.
3. Negative trading volumes.
4. Daily high below daily low.
5. 12-month high below 12-month low.
6. Day price outside the reported daily range.
7. Reported price change inconsistent with `day_price - previous`.

A tolerance of 0.02 was used for the price-change comparison, and 0.01 for the daily price-range comparison.

### Results

All 300,845 records were checked.

13 anomaly flags were identified:

| Issue | Flagged records |
|---|---:|
| Day price outside daily range | 12 |
| Zero previous price | 1 |
| **Total flags** | **13** |

No negative prices, negative volumes, inverted daily ranges, inverted 12-month ranges, or price-change calculation mismatches were flagged.

### Investigation of flagged records

Script:

```text
src/data_validation/investigate_market_integrity_flags.py
```

The 13 records were examined individually.

Findings:

- One Longhorn Kenya record from 2012 had a previous price of zero.
- Two 2018 records, for XPRS and UNGA, had day prices outside their reported daily ranges.
- Ten 2022 records had day prices outside their reported daily ranges.

A subsequent comparison against the original cleaned files confirmed that all 13 inconsistencies were already present in the source data.

Script:

```text
src/data_validation/compare_market_flags_with_source.py
```

### Data-handling decision

All 13 records were retained.

No values were corrected or replaced, and no records were deleted.

These inconsistencies are documented as source-level review flags.

Reports:

```text
reports/cleaning/
├── market_integrity_annual_summary.csv
├── market_integrity_issue_summary.csv
├── market_integrity_overall_summary.csv
├── market_integrity_anomaly_details.csv
├── market_integrity_zero_volume_summary.csv
├── market_integrity_investigation.csv
└── market_integrity_source_comparison.csv
```

---

# 8. Change Percentage Validation

An additional investigation was started to determine whether the source `Change%` column agrees with:

\[
\text{Expected Change \%} =
\frac{\text{Change}}{\text{Previous}}\times100
\]

Script:

```text
src/data_validation/validate_change_percentages.py
```

The first validation produced zero eligible records across all 19 years.

Therefore, no actual percentage comparisons were performed.

### Decision

The user elected to leave the `change_pct` column as it is.

- No recalculation was performed.
- No source values were replaced.
- No standardized datasets were modified.
- Percentage validation remains inconclusive.

This is a known limitation that must be considered before using `change_pct` as a machine-learning feature.

Reports:

```text
reports/cleaning/
├── change_percentage_annual_summary.csv
└── change_percentage_mismatches.csv
```

---

# 9. Combining the Standardized Datasets

The next processing stage is to combine the 19 annual standardized datasets into one historical NSE master dataset.

Script:

```text
src/data_cleaning/combine_standardized_datasets.py
```

Input files:

```text
data/processed/
├── 2007_standardized.csv
├── 2008_standardized.csv
├── 2009_standardized.csv
...
└── 2025_standardized.csv
```

### Planned processing

The script:

1. Loads all 19 annual standardized datasets.
2. Checks that every file contains the expected 13-column schema.
3. Checks that dates are valid.
4. Combines the annual records.
5. Sorts records chronologically by date and stock code.
6. Preserves repeated date/code records.
7. Checks the combined record count.
8. Saves the master dataset.
9. Generates annual and stock coverage reports.
10. Reloads the saved master dataset to verify its integrity.

### Expected output

```text
data/processed/nse_master_standardized.csv
```

Reports:

```text
reports/cleaning/
├── master_dataset_annual_coverage.csv
└── master_dataset_stock_coverage.csv
```

### Expected dataset characteristics

| Attribute | Expected value |
|---|---|
| Annual files | 19 |
| Total records | 300,845 |
| Columns | 13 |
| First date | 2007-01-02 |
| Last date | 2025-10-31 |
| Missing dates | 0 |
| Missing stock codes | 0 |

**Status:** Combining script prepared. Successful execution and verification are pending.

---

# 10. Important Data-Handling Decisions

The following decisions have been maintained throughout the preparation process.

| Area | Decision |
|---|---|
| Original raw files | Never modify |
| Exact duplicate rows | Remove additional identical copies |
| Repeated date/code records | Retain if other fields differ |
| Missing values | Preserve; do not automatically replace with zero |
| Completely blank rows | Remove and retain an audit copy |
| 2017 anomalous records | Exclude 70 from analytical data and preserve separately |
| Suspicious market values | Flag and investigate; do not automatically delete |
| Change percentage | Preserve without recalculation |
| Standardized datasets | Keep separate from cleaned datasets |
| Master dataset | Combine without losing annual records |

The purpose of these decisions is to preserve historical information and maintain a traceable data-processing process.

---

# 11. Current Data Status

The historical data preparation process has produced the following results:

| Metric | Result |
|---|---:|
| Original annual files | 19 |
| Original records | 301,005 |
| Exact duplicate copies removed | 88 |
| 2017 anomalous records excluded | 70 |
| Completely blank rows removed | 2 |
| Final standardized records | 300,845 |
| Standardized columns | 13 |
| Missing dates | 0 |
| Missing stock codes | 0 |
| Missing stock names | 48 |
| Market-integrity flags | 13 |

The 13 market-integrity flags are retained in the datasets and documented separately.

The 139 repeated date/code groups from 2009 are also retained.

---

# 12. Next Development Stages

After successfully creating and verifying the master dataset, development will continue in the following order.

## Stage 1: Complete historical data preparation

- Verify the master dataset.
- Review stock-code coverage.
- Examine historical trading frequency.
- Investigate missing values where necessary.

## Stage 2: Liquidity analysis

Classify securities into liquid and illiquid groups using measurable market activity.

Potential measures include:

- Trading frequency.
- Number of days traded.
- Average trading volume.
- Average traded value, where reliable.
- Consecutive periods without trading.

The classification methodology will be established before model training.

## Stage 3: Feature engineering

Develop time-series features such as:

- Daily returns.
- Lagged prices.
- Moving averages.
- Rolling volatility.
- Trading volume changes.
- Momentum indicators.
- Historical price trends.

Features must be constructed without using future information.

## Stage 4: Machine learning

Develop and compare:

- Baseline models.
- Random Forest.
- XGBoost.
- ARIMA.

The initial prediction objectives will include both price prediction and price-direction classification.

Models will be evaluated separately for liquid and illiquid securities.

## Stage 5: NSE financial news collection

Develop a news collection engine using:

- Kenyan financial news websites.
- Official NSE announcements.
- Company investor-relations announcements.
- Public RSS feeds.
- Relevant publicly accessible financial-market posts where collection is supported.

News will be linked to relevant listed companies and tickers.

## Stage 6: Sentiment analysis

Develop a news-processing pipeline to:

- Identify company mentions.
- Associate news with NSE stock codes.
- Classify sentiment.
- Identify significant company developments.
- Create time-based sentiment features.

## Stage 7: News-enhanced prediction models

Compare:

1. Models using historical market data only.
2. Models using historical market data and news-derived features.

This will help evaluate whether financial news provides additional predictive value.

## Stage 8: Web application

Develop the NSE intelligence and prediction platform using the planned web technology stack.

The application will eventually present:

- NSE-listed companies.
- Historical price information.
- Market statistics.
- Liquidity classifications.
- Prediction results.
- Financial news.
- Company sentiment.
- Model performance.

---

# 13. Reproducibility and Version Control

Git and GitHub will be used to track project development.

Important files to preserve include:

- Source Python scripts.
- README documentation.
- Dependency definitions.
- Data-processing decisions.
- Validation reports.
- Model code.
- Configuration examples.

The following should generally not be committed:

- `.venv/`
- `__pycache__/`
- `.pyc` files.
- Temporary files.
- Local secrets and API keys.

Historical CSV files and generated datasets should be considered separately when deciding what to upload, based on repository size and the source-data redistribution permissions.

A `.gitignore` file should exclude the virtual environment and local secrets.

---

# 14. Project Development Philosophy

The project follows a staged and evidence-based development approach.

1. Inspect before modifying.
2. Preserve original datasets.
3. Investigate anomalies before making corrections.
4. Keep cleaning, validation and feature engineering separate.
5. Generate reports for important processing decisions.
6. Verify outputs before proceeding.
7. Avoid data leakage in prediction models.
8. Compare models using consistent evaluation methods.
9. Document known limitations.
10. Build the web application after the underlying analytical pipeline is established.

The emphasis is on creating a reliable historical NSE dataset before attempting stock predictions.

---

## 15. Current Project Milestone

**Completed:** Historical dataset inspection, cleaning, duplicate handling, anomaly exclusion, date validation, blank-row removal, standardization, numeric conversion validation, and market-value integrity investigation.

**Current stage:** Combining the 19 standardized annual datasets into a single historical NSE master dataset.

**Next milestone:** Liquidity analysis and classification of NSE securities into liquid and illiquid groups.

Last documented data-processing total: **300,845 standardized records covering 2007–2025.**