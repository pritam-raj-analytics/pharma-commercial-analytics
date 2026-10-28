"""Public-evidence tiers for 37 oncology/neurosurgery centres (NCG-listed, 5 city groups).
Tier A = neurosurgery AND molecular pathology both publicly confirmed; B = one confirmed; C = neither confirmed.
'Not confirmed' means no adequate official source was found, NOT that the service is absent.
Usage: python access_gap.py data/centres_public_evidence.xlsx outputs/"""
import sys, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
df = pd.read_excel(sys.argv[1], sheet_name='Centres'); out = sys.argv[2]
neuro = df.iloc[:,3].astype(str).str.startswith('Yes'); mol = df.iloc[:,4].astype(str).str.startswith('Yes')
df['tier'] = ['A' if n and m else 'B' if n or m else 'C' for n, m in zip(neuro, mol)]
df['city_group'] = df['City'].replace({'Navi Mumbai':'Mumbai'})
t = df.groupby(['city_group','tier']).size().unstack(fill_value=0).reindex(columns=['A','B','C'], fill_value=0)
t['total'] = t.sum(axis=1); t.to_csv(f'{out}/access_gap_by_city.csv'); print(t.to_string())
print(f"\nCentres: {len(df)} | neurosurgery confirmed: {neuro.sum()} | molecular pathology confirmed: {mol.sum()} | both: {(neuro&mol).sum()}")
df[['Centre name','City','tier']].to_csv(f'{out}/centre_tiers.csv', index=False)
fig, ax = plt.subplots(figsize=(8,3.6)); t[['A','B','C']].plot.barh(stacked=True, ax=ax, color=['#2A9D8F','#E9C46A','#B8BEC9'], width=0.7)
ax.set_title('Public evidence of IDH-relevant capability, 37 listed centres', loc='left', fontsize=11)
ax.set_xlabel('Centres'); ax.set_ylabel(''); ax.legend(['A: both confirmed','B: one confirmed','C: neither confirmed'], frameon=False, fontsize=8)
for sp in ('top','right'): ax.spines[sp].set_visible(False)
fig.tight_layout(); fig.savefig(f'{out}/chart_access_gap.png', dpi=160)
