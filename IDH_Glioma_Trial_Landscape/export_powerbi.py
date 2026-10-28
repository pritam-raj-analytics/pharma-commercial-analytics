"""Write flat tables for Power BI / Excel: studies, sites, drugs.
Usage: python export_powerbi.py outputs/trials.db outputs/powerbi/"""
import sys, os, sqlite3, pandas as pd
db, out = sys.argv[1:3]; os.makedirs(out, exist_ok=True); con = sqlite3.connect(db)
for t in ['studies', 'sites', 'drugs']:
    pd.read_sql(f'SELECT * FROM {t}', con).to_csv(f'{out}/{t}.csv', index=False)
print('exported to', out)
