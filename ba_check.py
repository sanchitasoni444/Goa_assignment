import pandas as pd
from pathlib import Path
import sys


REQUIRED_ID_COLUMNS = [
    'state', 'year', 'month', 'district', 'fps_id', 'fps_name'
]


def main():
    csv_path = Path('data/processed/consolidated_fps_data.csv')
    if not csv_path.exists():
        print(f"Error: {csv_path} does not exist.")
        sys.exit(1)

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} records from {csv_path}.")
    issues = 0

    # Check 1: Required identity/metadata columns.
    for col in REQUIRED_ID_COLUMNS:
        if col not in df.columns:
            print(f"Warning: Required column {col} missing from consolidated data.")
            issues += 1

    # Check 2: Numeric fields should not contain negative values.
    numeric_cols = df.select_dtypes(include='number').columns
    for col in numeric_cols:
        negative_count = int((df[col] < 0).sum())
        if negative_count:
            print(f"Warning: {negative_count} records contain negative values in {col}.")
            issues += negative_count

    # Check 3: PHH/AAY ration-card counts should not both be zero when the
    # source table was successfully captured. Zero is allowed when the source
    # explicitly reports zero, so this is only a warning, not an automatic
    # failure, when no source-status flag is available.
    if 'phh_rc_total' in df.columns and 'aay_rc_total' in df.columns:
        missing_rc = df[(df['phh_rc_total'] == 0) & (df['aay_rc_total'] == 0)]
        if len(missing_rc) > 0:
            print(
                f"Warning: Found {len(missing_rc)} records with 0 for both "
                "PHH and AAY ration card counts."
            )
            issues += len(missing_rc)

    # Check 4: If the consolidated output contains commodity totals, verify
    # that component quantities reconcile to the recorded total.
    quantity_components = [
        'wheat_total_kg',
        'fortified_rice_total_kg',
        'rice_total_kg',
        'coarse_grains_total_kg',
    ]
    quantity_total = 'total_total_kg'
    if all(c in df.columns for c in quantity_components) and quantity_total in df.columns:
        calculated_total = df[quantity_components].sum(axis=1)
        mismatches = df[(calculated_total - df[quantity_total]).abs() > 0.1]
        if len(mismatches) > 0:
            print(
                f"Warning: Found {len(mismatches)} records where calculated "
                "commodity quantities do not match the recorded total."
            )
            issues += len(mismatches)

    # Check 5: Respect explicit inconsistency flags emitted by consolidation.
    flag_cols = [c for c in df.columns if c.startswith('flag_')]
    for col in flag_cols:
        flagged = df[col].fillna(False).astype(bool)
        count = int(flagged.sum())
        if count:
            print(f"Warning: {count} records flagged by {col}.")
            issues += count

    if issues == 0:
        print("Business Analyst Check: PASSED. No structural anomalies found in the dataset.")
    else:
        print(f"Business Analyst Check: {issues} warnings found. Please review the dataset.")
        sys.exit(1)


if __name__ == '__main__':
    main()
