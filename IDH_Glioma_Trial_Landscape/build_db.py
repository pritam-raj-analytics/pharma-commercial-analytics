"""Load the ClinicalTrials.gov export into SQLite and derive helper tables.
Usage: python build_db.py outputs/trials.db data/file1.csv [data/file2.csv ...]
Several exports are merged and de-duplicated on NCT number."""
import sys, re, sqlite3, pandas as pd

dbpath, srcs = sys.argv[1], sys.argv[2:]
df = pd.concat([pd.read_csv(f) for f in srcs]).drop_duplicates('NCT Number')
df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]

# --- dates: registry gives YYYY-MM-DD or YYYY-MM; keep the year
df['start_year'] = pd.to_numeric(df['start_date'].str[:4], errors='coerce')

# --- IDH-inhibitor programmes (name + aliases). Extend as new agents appear.
INHIBITORS = {
    'Vorasidenib':  r'vorasidenib|AG-?881|S095032',
    'Safusidenib':  r'safusidenib|DS-?1001',
    'Ivosidenib':   r'ivosidenib|AG-?120',
    'Olutasidenib': r'olutasidenib|FT-?2102',
    'HMPL-306':     r'HMPL-?306',
    'IDH305':       r'IDH305',
    'LY3410738':    r'LY3410738',
    'Enasidenib':   r'enasidenib|AG-?221',
}
text = (df['study_title'].fillna('') + ' ' + df['interventions'].fillna('') + ' ' +
        df['brief_summary'].fillna(''))
df['idh_related'] = text.str.contains(r'\bIDH|isocitrate', case=False, regex=True).astype(int)

# --- sponsor groups: collapse name variants of the same organisation
SPONSOR_GROUPS = [('Servier', r'servier'), ('Daiichi Sankyo', r'daiichi'),
                  ('Nuvation Bio', r'nuvation'), ('NCI / NIH', r'national cancer institute|nci\b'),
                  ('Hutchmed', r'hutchmed|hutchison')]
def group(x):
    for g, p in SPONSOR_GROUPS:
        if re.search(p, str(x), flags=re.I): return g
    return x
df['sponsor_group'] = df['sponsor'].map(group)

# --- sites: one row per location; country = last comma-separated token
rows = []
for nct, loc in zip(df['nct_number'], df['locations'].fillna('')):
    for site in [s.strip() for s in loc.split('|') if s.strip()]:
        rows.append((nct, site, site.split(',')[-1].strip()))
sites = pd.DataFrame(rows, columns=['nct_number', 'site', 'country'])

# --- drug programmes per trial (exact word match; avoids e.g. 'Indiana'-style false hits)
drug_rows = []
drug_text = df['interventions'].fillna('')
drug_text = drug_text.where(drug_text.str.strip() != '', df['study_title'].fillna(''))
for nct, t in zip(df['nct_number'], drug_text):
    for name, pat in INHIBITORS.items():
        if re.search(pat, t, flags=re.I):
            drug_rows.append((nct, name))
drugs = pd.DataFrame(drug_rows, columns=['nct_number', 'drug'])

keep = ['nct_number','study_title','study_status','study_type','phases','enrollment','sponsor','sponsor_group',
        'funder_type','start_date','start_year','primary_completion_date','conditions',
        'interventions','idh_related','study_url']
con = sqlite3.connect(dbpath)
df[keep].to_sql('studies', con, if_exists='replace', index=False)
sites.to_sql('sites', con, if_exists='replace', index=False)
drugs.to_sql('drugs', con, if_exists='replace', index=False)
con.close()
print(f"studies={len(df)} sites={len(sites)} drug_links={len(drugs)}")
