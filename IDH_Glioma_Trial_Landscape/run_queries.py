"""Run every query in sql/queries.sql and write one CSV per query (Power BI-ready).
Usage: python run_queries.py outputs/trials.db sql/queries.sql outputs/"""
import sys, sqlite3, pandas as pd
db, sqlf, out = sys.argv[1:4]
con = sqlite3.connect(db)
blocks = [b.strip() for b in open(sqlf).read().split('-- Q') if b.strip()]
for b in blocks:
    head, _, body = b.partition('\n')
    n = head.split(':')[0]
    df = pd.read_sql(body, con)
    df.to_csv(f"{out}/q{n}.csv", index=False)
    print(f"\n== Q{n}: {head.split(':',1)[1].strip()}\n{df.to_string(index=False, max_colwidth=60)}")
