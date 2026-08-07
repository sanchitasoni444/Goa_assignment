import os
import json
import pandas as pd
from pathlib import Path

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
    # filepath like data/raw/2026_03/north_goa/158500100001_158500100001___NAME.json
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
    
    tables = data.get('tables', {})
    
    # Extract "Number of Transacted Ration Cards"
    rc_table = tables.get('Number of Transacted Ration Cards', [])
    if rc_table and len(rc_table) > 1:
        for r in rc_table[1:]:
            if len(r) >= 5:
                card_type = r[0].replace('\n', '').replace('\t', '').strip()
                if 'PHH' in card_type:
                    row['phh_rc_total'] = clean_number(r[4])
                elif 'AAY' in card_type:
                    row['aay_rc_total'] = clean_number(r[4])
                    
    # Find Transactions and Quantity tables dynamically
    for t_key, table in tables.items():
        if not table or not isinstance(table, list) or len(table) < 2:
            continue
            
        header = table[0]
        if len(header) >= 5 and header[0].strip() == 'Commodity':
            is_txn_table = 'Regular Txn' in header[1]
            is_qty_table = 'Regular' in header[1] and 'Txn' in header[1] and not is_txn_table # fallback or distinct
            
            if header[1].strip() == 'Regular Txn':
                prefix = 'txn_'
            else:
                prefix = 'qty_'
                
            for r in table[1:]:
                if len(r) >= 5:
                    commodity = r[0].strip().lower().replace(' ', '_')
                    row[f'{prefix}{commodity}_total'] = clean_number(r[4])

    return row

def main():
    base_dir = Path('data/raw')
    all_rows = []
    
    if not base_dir.exists():
        print("Raw data directory not found.")
        return
        
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.json'):
                filepath = os.path.join(root, file)
                try:
                    row = process_file(filepath)
                    all_rows.append(row)
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
                    
    if not all_rows:
        print("No data extracted.")
        return
        
    df = pd.DataFrame(all_rows)
    
    # Reorder columns to have primary keys first
    cols = ['year_month', 'district', 'fps_id', 'fps_name_slug']
    other_cols = [c for c in df.columns if c not in cols]
    df = df[cols + sorted(other_cols)]
    
    out_dir = Path('data/processed')
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / 'consolidated_fps_data.csv'
    
    df.fillna(0, inplace=True)
    df.to_csv(out_path, index=False)
    print(f"Successfully consolidated {len(df)} records into {out_path}")

if __name__ == '__main__':
    main()
