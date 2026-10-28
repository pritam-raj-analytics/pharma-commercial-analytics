"""Create the three README charts from the SQLite database.
Usage: python make_charts.py outputs/trials.db outputs/"""
import sys, sqlite3, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
db, out = sys.argv[1:3]; con = sqlite3.connect(db)
NAVY, TEAL, GREY, RED = '#1F3864', '#2A9D8F', '#B8BEC9', '#C0392B'
plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False})

# 1. IDH trials started per year (planned starts shaded)
y = pd.read_sql("SELECT start_year, COUNT(*) n FROM studies WHERE idh_related=1 AND start_year BETWEEN 2014 AND 2027 GROUP BY 1", con)
fig, ax = plt.subplots(figsize=(8,3.8))
ax.bar(y.start_year, y.n, color=[GREY if v>2026 else NAVY for v in y.start_year])
ax.set_title('IDH-related glioma trials by start year (registry start date)', loc='left', fontsize=12)
ax.set_ylabel('Trials'); ax.set_xticks(y.start_year); ax.tick_params(axis='x', rotation=45)
fig.text(0.01, 0.01, 'Grey = not-yet-started trials with a planned start date. Source: ClinicalTrials.gov exports, accessed 27 Oct 2026.', fontsize=7)
fig.tight_layout(rect=(0,0.03,1,1)); fig.savefig(f'{out}/chart1_trials_per_year.png', dpi=160); plt.close()

# 2. Pipeline by drug: live vs finished
d = pd.read_sql("""SELECT dr.drug, SUM(CASE WHEN s.study_status IN ('RECRUITING','NOT_YET_RECRUITING','ACTIVE_NOT_RECRUITING','ENROLLING_BY_INVITATION') THEN 1 ELSE 0 END) live,
 SUM(CASE WHEN s.study_status NOT IN ('RECRUITING','NOT_YET_RECRUITING','ACTIVE_NOT_RECRUITING','ENROLLING_BY_INVITATION') THEN 1 ELSE 0 END) other
 FROM drugs dr JOIN studies s USING(nct_number) WHERE dr.drug!='Enasidenib' GROUP BY dr.drug ORDER BY live+other""", con)
fig, ax = plt.subplots(figsize=(8,3.8))
ax.barh(d.drug, d.live, color=TEAL, label='Live (recruiting / not yet / active)')
ax.barh(d.drug, d.other, left=d.live, color=GREY, label='Completed, withdrawn, unknown or other')
ax.set_title('IDH-inhibitor programmes in glioma trials: live vs other', loc='left', fontsize=12)
ax.set_xlabel('Trials'); ax.legend(frameon=False, fontsize=8, loc='lower right')
fig.tight_layout(); fig.savefig(f'{out}/chart2_pipeline_by_drug.png', dpi=160); plt.close()

# 3. Countries by number of trials; India highlighted
c = pd.read_sql("""SELECT st.country, COUNT(DISTINCT st.nct_number) n FROM sites st JOIN studies s USING(nct_number)
 WHERE s.idh_related=1 GROUP BY 1 ORDER BY n DESC LIMIT 10""", con)
ind = pd.read_sql("SELECT COUNT(DISTINCT st.nct_number) n FROM sites st JOIN studies s USING(nct_number) WHERE s.idh_related=1 AND st.country='India'", con).n[0]
c = pd.concat([c, pd.DataFrame({'country':['India'],'n':[ind]})]).iloc[::-1]
fig, ax = plt.subplots(figsize=(8,4.2))
ax.barh(c.country, c.n, color=[RED if k=='India' else NAVY for k in c.country])
for i,(k,v) in enumerate(zip(c.country,c.n)): ax.text(v+0.4, i, str(v), va='center', fontsize=8)
ax.set_title('Trials with at least one site, by country (top 10 + India)', loc='left', fontsize=12)
ax.set_xlabel('Distinct trials')
fig.tight_layout(); fig.savefig(f'{out}/chart3_countries.png', dpi=160); plt.close()

tot = pd.read_sql("SELECT COUNT(*) n, SUM(study_type='INTERVENTIONAL') i, SUM(idh_related) idh FROM studies", con)
print(tot.to_string(index=False), '| India trials among IDH-related:', ind)
