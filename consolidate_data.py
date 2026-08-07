import os
import json
import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_number(val):
    if not isinstance(val, str):
        return val
    val = val.replace(',', '').strip()
    if not val:
        return 0.0
    try:
        return float(val)
    except ValueError:
        return 0.0

def process_file(filepath):
    path = Path(filepath)
    filename = path.name
    district = path.parent.name
    year_month = path.parent.parent.name
    
    fps_id = filename.split('_')[0]
    fps_name = filename.replace('.json', '')
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    row = {
        'year_month': year_month,
        'district': district,
        'fps_id': fps_id,
        'fps_name_slug': fps_name
    }
    
    summary = data.get('summary', {})
    tables = data.get('tables', {})
    
    # Inconsistency Check 1: Missing Summary or Tables
    if not summary:
        logger.warning(f"INCONSISTENCY FLAG: {fps_id} is missing summary cards.")
    if not tables:
        logger.warning(f"INCONSISTENCY FLAG: {fps_id} is missing all tables.")
        
    # Extract Summary Data
    for key, val in summary.items():
        clean_key = key.lower().replace('-', '_').replace(' ', '_').replace('(', '').replace(')', '')
        row[f"summary_{clean_key}"] = clean_number(val)

    # Inconsistency Check 2: Zero Transactions
    total_txn = row.get('summary_total_e_transaction', 0)
    if total_txn == 0:
        logger.warning(f"INCONSISTENCY FLAG: {fps_id} has 0 Total e-Transactions recorded in summary.")

    # Extract "Number of Transacted Ration Cards"
    rc_table = tables.get('Number of Transacted Ration Cards', [])
    if rc_table and len(rc_table) > 1:
        for r in rc_table[1:]:
            if len(r) >= 5:
                card_type = r[0].replace('\n', '').replace('\t', '').strip()
                if 'PHH' in card_type:
                    row['phh_rc_regular'] = clean_number(r[1])
                    row['phh_rc_intra'] = clean_number(r[2])
                    row['phh_rc_inter'] = clean_number(r[3])
                    row['phh_rc_total'] = clean_number(r[4])
                elif 'AAY' in card_type:
                    row['aay_rc_regular'] = clean_number(r[1])
                    row['aay_rc_intra'] = clean_number(r[2])
                    row['aay_rc_inter'] = clean_number(r[3])
                    row['aay_rc_total'] = clean_number(r[4])
    else:
        logger.warning(f"INCONSISTENCY FLAG: {fps_id} is missing the Number of Transacted Ration Cards table.")

    # Find Transactions and Quantity tables dynamically
    found_txn = False
    found_qty = False
    for t_key, table in tables.items():
        if not table or not isinstance(table, list) or len(table) < 2:
            continue
            
        header = table[0]
        if len(header) >= 5 and header[0].strip() == 'Commodity':
            if header[1].strip() == 'Regular Txn':
                prefix = 'txn_'
                found_txn = True
            else:
                prefix = 'qty_'
                found_qty = True
                
            for r in table[1:]:
                if len(r) >= 5:
                    commodity = r[0].strip().lower().replace(' ', '_')
                    row[f'{prefix}{commodity}_regular'] = clean_number(r[1])
                    row[f'{prefix}{commodity}_intra'] = clean_number(r[2])
                    row[f'{prefix}{commodity}_inter'] = clean_number(r[3])
                    row[f'{prefix}{commodity}_total'] = clean_number(r[4])
                    
    if not found_txn:
         logger.warning(f"INCONSISTENCY FLAG: {fps_id} is missing the Transactions table.")
    if not found_qty:
         logger.warning(f"INCONSISTENCY FLAG: {fps_id} is missing the Distributed Quantity table.")

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
    
    cols = ['year_month', 'district', 'fps_id', 'fps_name_slug']
    other_cols = [c for c in df.columns if c not in cols]
    df = df[cols + sorted(other_cols)]
    
    out_dir = Path('data/processed')
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / 'consolidated_fps_data.csv'
    
    df.fillna(0, inplace=True)
    df.to_csv(out_path, index=False)
    logger.info(f"Successfully consolidated {len(df)} records into {out_path}")

if __name__ == '__main__':
    main()
