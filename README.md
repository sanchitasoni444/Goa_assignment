# Goa FPS Data Pipeline

An automated data scraping and consolidation pipeline designed to extract transaction metrics for Fair Price Shops (FPS) from the IMPDS web portal.

## Approach

This project extracts dynamically loaded FPS-level data and transforms it into a standardized tabular format for downstream business analysis.

The pipeline is divided into three scripts:

1. **`get_raw_data.py`**: A Selenium-based web scraper that navigates through Goa, North Goa, and South Goa for March 2026 and April 2026. It enumerates **all FPS returned by the IMPDS portal for each target district/month** and saves each FPS response as an individual raw JSON document.
2. **`consolidate_data.py`**: A data transformation script that parses the raw JSON outputs, flattens the hierarchical transaction/ration-card/commodity tables, standardizes numeric values, and writes the analysis-ready dataset to `data/processed/consolidated_fps_data.csv`.
3. **`ba_check.py`**: A validation script that checks required metadata, numeric integrity, PHH/AAY ration-card counts, optional commodity-total reconciliation, and explicit inconsistency flags emitted by the consolidation step.

## Data Coverage

- State: Goa
- Districts: North Goa and South Goa
- Months: March 2026 and April 2026
- FPS coverage: all FPS returned by the portal for each district/month when the scraper is run

The repository's checked-in processed CSV is a generated output artifact. After changing the scraper or raw data, regenerate it with `python consolidate_data.py` so that the processed file reflects the complete raw dataset.

## Assumptions Made

- The target DOM structure remains consistent across the selected months and districts.
- Elements are loaded dynamically via AJAX, so explicit waits are used before extraction.
- The six coarse-grain sub-commodities (Barley, Bajra, Maize, Jowar, Ragi, Kodo) may be nested and are tracked explicitly during consolidation.
- Missing source values are treated as unavailable during extraction and are represented consistently by the consolidation step.

## How to Run the Code

### 1. Prerequisites

Ensure Python 3.9+ and Microsoft Edge are installed, then install the required dependencies:

```bash
pip install -r requirements.txt
```

### 2. Running the Scraper

Execute the data collection script:

```bash
python get_raw_data.py
```

This launches a headless Edge browser and populates `data/raw/` with one JSON file per FPS/month.

### 3. Consolidating the Data

Once raw data collection is complete:

```bash
python consolidate_data.py
```

The final output is written to:

```text
data/processed/consolidated_fps_data.csv
```

### 4. Running the Quality Check

```bash
python ba_check.py
```

The validation script exits successfully only when no configured data-quality issues are detected.

## Known Limitations

- The scraper currently hardcodes the target months (March 2026, April 2026) and state (Goa) for the scope of this assignment.
- Network instability or rate-limiting by the NIC portal can cause timeouts. The scraper uses retry logic and avoids aggressive parallelization.
- The scraper relies on Edge WebDriver. Microsoft Edge must be installed locally.
- Because the source portal is dynamically rendered, minor DOM changes on IMPDS may require selector updates.
