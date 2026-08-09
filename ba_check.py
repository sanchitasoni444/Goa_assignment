import pandas as pd
from pathlib import Path
import sys


def main():
    csv_path = Path('data/processed/consolidated_fps_data.csv')
    if not csv_path.exists():
        print(f"Error: {csv_path} does not exist.")
        sys.exit(1)

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} records from {csv_path}.")

    issues = 0

    # Check 1: Ensure all expected commodities are present.
    expected_cols = [
        'qty_wheat_total', 'qty_fortified_rice_total', 'qty_rice_total',
        'qty_coarse_grains_total'
    ]

    for col in expected_cols:
        if col not in df.columns:
            print(f"Warning: Expected column {col} missing from consolidated data.")
            issues += 1

    # Check 2: Total quantity consistency.
    if all(c in df.columns for c in expected_cols) and 'qty_total_total' in df.columns:
        calculated_total = (
            df['qty_wheat_total']
            + df['qty_fortified_rice_total']
            + df['qty_rice_total']
            + df['qty_coarse_grains_total']
        )
        mismatches = df[(calculated_total - df['qty_total_total']).abs() > 0.1]

        if len(mismatches) > 0:
            print(
                f"Warning: Found {len(mismatches)} records where calculated sum "
                "of components doesn't match total distributed quantity."
            )
            issues += len(mismatches)

    # Check 3: Missing PHH/AAY counts.
    if 'phh_rc_total' in df.columns and 'aay_rc_total' in df.columns:
        missing_rc = df[(df['phh_rc_total'] == 0) & (df['aay_rc_total'] == 0)]
        if len(missing_rc) > 0:
            print(
                f"Warning: Found {len(missing_rc)} records with 0 for both "
                "PHH and AAY ration card counts."
            )
            # Count every affected record so the final status cannot report
            # PASSED when this validation actually found anomalies.
            issues += len(missing_rc)

    # Check 4: Explicit inconsistency flags emitted by consolidation.
    flag_cols = [c for c in df.columns if c.startswith('flag_')]
    for col in flag_cols:
        flagged = df[col].fillna(False).astype(bool)
        if flagged.any():
            count = int(flagged.sum())
            print(f"Warning: {count} records flagged by {col}.")
            issues += count

    if issues == 0:
        print("Business Analyst Check: PASSED. No structural anomalies found in the dataset.")
    else:
        print(f"Business Analyst Check: {issues} warnings found. Please review the dataset.")
        sys.exit(1)


if __name__ == '__main__':
    main()
