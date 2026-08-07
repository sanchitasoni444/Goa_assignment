# Goa FPS Data Pipeline

An automated data scraping and consolidation pipeline designed to extract state-level transaction metrics for Fair Price Shops (FPS) from the IMPDS web portal. 

## Approach
This project tackles the extraction of deeply nested, dynamically loaded transaction data and transforms it into a standardized tabular format for downstream business analysis. 
The pipeline is divided into two primary scripts:

1. **`get_raw_data.py`**: A Selenium-based web scraper that navigates through the state (Goa) and district-level (North Goa, South Goa) directories. It iterates through the months (March 2026, April 2026) to enumerate all active Fair Price Shops. It extracts data from complex modal tables, including parsing out sub-commodity distributions like Coarse Grains, and saves the raw output as individual JSON documents.
2. **`consolidate_data.py`**: A data transformation script that parses the directory structure containing the raw JSON outputs. It flattens the hierarchical data structures and standardizes string-based numerics into floats, merging all metrics into a single analysis-ready format (`data/processed/consolidated_fps_data.csv`).
3. **`ba_check.py`**: A data validation script that audits the final consolidated dataset to ensure structural integrity and mathematical consistency (e.g., verifying that individual commodity distributions correctly sum to the recorded total limits).

## Assumptions Made
- The target DOM structure remains consistent across different months and districts.
- Elements are loaded dynamically via AJAX, so implicit and explicit waits are required before extracting elements.
- The 6 coarse grains sub-commodities (Barley, Bajra, Maize, Jowar, Ragi, Kodo) are nested and must be expanded via DOM interaction to be scraped.
- For missing tables or data values, a value of 0.0 or a blank string is an acceptable fallback.

## How to Run the Code

### 1. Prerequisites
Ensure you have Python 3.9+ installed and clone this repository.
Install the required dependencies:
```bash
pip install -r requirements.txt
```

### 2. Running the Scraper
Execute the data collection script to scrape the raw JSON data.
```bash
python get_raw_data.py
```
*Note: This will launch a headless Edge browser and populate the `data/raw/` directory.*

### 3. Consolidating the Data
Once the raw data is collected, run the consolidation script to flatten it into a CSV.
```bash
python consolidate_data.py
```
*The final output will be generated at `data/processed/consolidated_fps_data.csv`.*

### 4. Running the Quality Check
Verify the integrity of the consolidated dataset.
```bash
python ba_check.py
```

## Known Limitations
- The scraper currently hardcodes the target months (March 2026, April 2026) and state (Goa) directly in the script for the scope of this assignment.
- Network instability or rate-limiting by the NIC portal can cause timeouts. The scraper has basic retry logic, but heavy parallelization is avoided to prevent IP blocks.
- The scraper relies on Edge WebDriver. You must have Microsoft Edge installed on your local machine.
