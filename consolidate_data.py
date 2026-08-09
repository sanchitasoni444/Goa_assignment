"""
consolidate_data.py

Combines every FPS-level raw JSON record (data/raw/<year-month>/<district>/*.json)
into a single analysis-ready CSV at data/processed/consolidated_fps_data.csv,
with one row per FPS per month.

--------------------------------------------------------------------------
FIXES APPLIED (relative to the previous version):
  1. The "Number of Transactions" table (PHH/AAY rows, Regular/Intra/Inter/
     Total columns) is now explicitly flattened into columns. Previously
     the dynamic table-detection loop only matched tables whose header
     started with "Commodity" — true only for the Distributed Quantity
     table — so the transaction counts were silently dropped from the CSV.
  2. year / month / state / district / fps_id / fps_name are now read
     directly from the JSON record when present (the fixed scraper embeds
     them), falling back to path-based parsing for older raw files that
     don't have these fields.
  3. Handles both `data/raw/2026-03/...` (new) and `data/raw/2026_03/...`
     (legacy) year-month folder naming.
  4. Inconsistency checks are now also written out as explicit boolean
     flag_* columns on each row, not just log lines, so they're usable
     downstream without re-parsing logs.
  5. A dedicated flag_coarse_grains_not_expanded column reports whether all
     six Coarse Grains sub-commodities (Barley, Bajra, Maize, Jowar, Ragi,
     Kodo) made it into the row, vs. just a collapsed total.
  6. Consistent column naming scheme for flattened tables:
       {group}_{regular|intra_state|inter_state|total}_{txn|ration_card}
       {commodity}_{regular|intra_state|inter_state|total}_kg
--------------------------------------------------------------------------
"""

import os
import re
import json
import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

COLUMN_SUFFIXES = ["regular", "intra_state", "inter_state", "total"]


def clean_number(val):
    """Strip commas/whitespace and coerce to float; blanks -> 0.0."""
    if val is None:
        return 0.0
    if not isinstance(val, str):
        try:
            return float(val)
        except (TypeError, ValueError):
            return 0.0
    val = val.replace(',', '').strip()
    if not val:
        return 0.0
    try:
        return float(val)
    except ValueError:
        return 0.0


def parse_path_metadata(filepath):
    """
    Fallback metadata extraction from the folder/file structure, for raw
    files that predate embedded metadata:
        data/raw/<year-month>/<district_slug>/<fps_id>_<fps_name>.json
    Supports both '2026-03' and '2026_03' year-month folder naming.
    """
    path = Path(filepath)
    filename = path.name
    district_slug = path.parent.name
    year_month_raw = path.parent.parent.name

    m = re.match(r"(\d{4})[-_](\d{2})", year_month_raw)
    year, month = (m.group(1), m.group(2)) if m else (year_month_raw, "")

    fps_id = filename.split('_', 1)[0]
    fps_name_slug = filename.replace('.json', '')
    fps_name = fps_name_slug.split('_', 1)[-1].replace('_', ' ') if '_' in fps_name_slug else fps_name_slug

    return {
        "year": year,
        "month": month,
        "state": "Goa",
        "district": district_slug.replace('_', ' ').title(),
        "fps_id": fps_id,
        "fps_name": fps_name,
    }


def flatten_group_table(table, prefix_map, suffix_label, row, flag_key):
    """
    Flatten a table shaped like:
        [Header, Regular, Intra State, Inter State, Total]
        [PHH,    ..,      ..,          ..,          ..   ]
        [AAY,    ..,      ..,          ..,          ..   ]
    `prefix_map` maps a row-label substring (e.g. 'PHH') to the column
    prefix to use (e.g. 'phh'). `suffix_label` is appended to each column
    name, e.g. 'txn' or 'ration_card'. Sets row[flag_key] = True if no
    expected rows were found (table missing / didn't load / empty).
    """
    found_any = False
    if not table or len(table) < 2:
        row[flag_key] = True
        return

    for r in table[1:]:
        if len(r) < 5:
            continue
        row_label = r[0].replace('\n', '').replace('\t', '').strip().upper()
        matched_prefix = next(
            (col_prefix for label_substr, col_prefix in prefix_map.items() if label_substr in row_label),
            None,
        )
        if not matched_prefix:
            continue
        found_any = True
        for suffix, val in zip(COLUMN_SUFFIXES, r[1:5]):
            row[f"{matched_prefix}_{suffix}_{suffix_label}"] = clean_number(val)

    row[flag_key] = not found_any


def flatten_quantity_table(table, row, flag_key):
    """
    Flatten the Distributed Quantity table (commodity rows, including the
    six expanded Coarse Grains sub-commodities) into columns like
    rice_regular_kg, barley_intra_state_kg, etc.
    """
    found_any = False
    if not table or len(table) < 2:
        row[flag_key] = True
        return

    for r in table[1:]:
        if len(r) < 5:
            continue
        commodity = r[0].strip().lower().replace(' ', '_')
        if not commodity:
            continue
        found_any = True
        for suffix, val in zip(COLUMN_SUFFIXES, r[1:5]):
            row[f"{commodity}_{suffix}_kg"] = clean_number(val)

    row[flag_key] = not found_any


def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Prefer metadata embedded by the (fixed) scraper; fall back to
    # path-based parsing for older raw files that lack these fields.
    required_keys = ("year", "month", "state", "district", "fps_id", "fps_name")
    if all(k in data for k in required_keys):
        meta = {k: data[k] for k in required_keys}
    else:
        meta = parse_path_metadata(filepath)

    fps_id = meta["fps_id"]
    row = dict(meta)  # year, month, state, district, fps_id, fps_name

    summary = data.get('summary', {})
    tables = data.get('tables', {})

    # --- Inconsistency flags (explicit columns, not just log lines) ---
    row["flag_missing_summary"] = not bool(summary)
    row["flag_missing_all_tables"] = not bool(tables)

    if row["flag_missing_summary"]:
        logger.warning(f"INCONSISTENCY FLAG: {fps_id} is missing summary cards.")
    if row["flag_missing_all_tables"]:
        logger.warning(f"INCONSISTENCY FLAG: {fps_id} is missing all tables.")

    # --- Summary cards ---
    for key, val in summary.items():
        clean_key = key.lower().replace('-', '_').replace(' ', '_').replace('(', '').replace(')', '')
        row[f"summary_{clean_key}"] = clean_number(val)

    total_txn = row.get('summary_total_e_transaction', 0)
    row["flag_zero_transactions"] = (total_txn == 0)
    if row["flag_zero_transactions"]:
        logger.warning(f"INCONSISTENCY FLAG: {fps_id} has 0 Total e-Transactions recorded in summary.")

    # --- Number of Transactions table (PHH/AAY, Regular/Intra/Inter/Total) ---
    # FIX: this table was previously never flattened into the CSV at all —
    # the old dynamic-table loop only matched Commodity-keyed tables.
    flatten_group_table(
        tables.get('Number of Transactions', []),
        prefix_map={"PHH": "phh", "AAY": "aay"},
        suffix_label="txn",
        row=row,
        flag_key="flag_missing_txn_table",
    )
    if row["flag_missing_txn_table"]:
        logger.warning(f"INCONSISTENCY FLAG: {fps_id} is missing the Number of Transactions table.")

    # --- Number of Transacted Ration Cards table ---
    flatten_group_table(
        tables.get('Number of Transacted Ration Cards', []),
        prefix_map={"PHH": "phh", "AAY": "aay"},
        suffix_label="ration_card",
        row=row,
        flag_key="flag_missing_rc_table",
    )
    if row["flag_missing_rc_table"]:
        logger.warning(f"INCONSISTENCY FLAG: {fps_id} is missing the Number of Transacted Ration Cards table.")

    # --- Distributed Quantity table (incl. expanded Coarse Grains rows) ---
    flatten_quantity_table(
        tables.get('Distributed Quantity', []),
        row=row,
        flag_key="flag_missing_qty_table",
    )
    if row["flag_missing_qty_table"]:
        logger.warning(f"INCONSISTENCY FLAG: {fps_id} is missing the Distributed Quantity table.")

    # Flag if Coarse Grains wasn't actually expanded into its six
    # sub-commodities during scraping (only a collapsed total made it in).
    expected_subcommodities = {"barley", "bajra", "maize", "jowar", "ragi", "kodo"}
    found_subcommodities = {c for c in expected_subcommodities if f"{c}_total_kg" in row}
    row["flag_coarse_grains_not_expanded"] = len(found_subcommodities) < len(expected_subcommodities)
    if row["flag_coarse_grains_not_expanded"]:
        logger.warning(f"INCONSISTENCY FLAG: {fps_id} does not have all 6 Coarse Grains sub-commodities.")

    return row


def main():
    base_dir = Path('data/raw')
    all_rows = []

    if not base_dir.exists():
        logger.error("Raw data directory not found.")
        return

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.json'):
                filepath = os.path.join(root, file)
                try:
                    row = process_file(filepath)
                    all_rows.append(row)
                except Exception as e:
                    logger.error(f"Error processing {filepath}: {e}")

    if not all_rows:
        logger.error("No data extracted.")
        return

    df = pd.DataFrame(all_rows)

    id_cols = [c for c in ["year", "month", "state", "district", "fps_id", "fps_name"] if c in df.columns]
    flag_cols = sorted(c for c in df.columns if c.startswith("flag_"))
    other_cols = sorted(c for c in df.columns if c not in id_cols and c not in flag_cols)
    df = df[id_cols + flag_cols + other_cols]

    # Only fill numeric measurement columns with 0.0 — never touch id/flag columns.
    df[other_cols] = df[other_cols].fillna(0.0)

    out_dir = Path('data/processed')
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / 'consolidated_fps_data.csv'
    df.to_csv(out_path, index=False)
    logger.info(f"Successfully consolidated {len(df)} records into {out_path}")


if __name__ == '__main__':
    main()
