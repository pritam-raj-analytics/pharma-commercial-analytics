"""IDH-mutant grade 2 glioma patient funnel for India: low / base / high scenarios + one-at-a-time sensitivity.
Usage: python model.py data/assumptions.csv outputs/"""
import sys, pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
a = pd.read_csv(sys.argv[1]).set_index('key'); out = sys.argv[2]
NAVY, TEAL, GREY, RED = '#1F3864', '#2A9D8F', '#B8BEC9', '#C0392B'
plt.rcParams.update({'axes.spines.top':False,'axes.spines.right':False})

def funnel(p):
    s = {}
    s['Malignant brain/CNS tumours']          = p['cns_cases']
    s['Gliomas']                              = s['Malignant brain/CNS tumours'] * p['glioma_share']
    s['Grade 2 diffuse gliomas']              = s['Gliomas'] * p['g2_share']
    s['IDH-mutant grade 2']                   = s['Grade 2 diffuse gliomas'] * p['idh_mut']
    s['IDH-mutant, identified by testing']    = s['IDH-mutant grade 2'] * p['test_rate'] * p['detect']
    s['Identified and INDIGO-type eligible']  = s['IDH-mutant, identified by testing'] * p['window']
    return s

def params(col):  return a[col].to_dict()
scen = pd.DataFrame({c: funnel(params(c)) for c in ['low','base','high']}).round(0).astype(int)
scen.index.name = 'step'; scen.to_csv(f'{out}/funnel_scenarios.csv')
print(scen.to_string())

# Steady-state pool = annual identified & eligible x years on treatment
pool = {c: scen.loc['Identified and INDIGO-type eligible', c] * a.loc['duration', c] for c in ['low','base','high']}
print('\nSteady-state eligible patients on therapy:', {k: round(v) for k, v in pool.items()})

# One-at-a-time sensitivity on the final funnel step (annual identified & eligible patients)
base = params('base'); ref = funnel(base)['Identified and INDIGO-type eligible']; rows = []
for k in ['glioma_share','g2_share','idh_mut','test_rate','detect','window']:
    lo = funnel({**base, k: a.loc[k,'low']})['Identified and INDIGO-type eligible']
    hi = funnel({**base, k: a.loc[k,'high']})['Identified and INDIGO-type eligible']
    rows.append((a.loc[k,'parameter'], lo, hi, hi-lo))
sens = pd.DataFrame(rows, columns=['parameter','at_low','at_high','swing']).sort_values('swing', ascending=False)
sens.round(0).to_csv(f'{out}/sensitivity.csv', index=False); print('\nBase =', round(ref)); print(sens.round(0).to_string(index=False))

# Chart 1: base-case funnel
b = scen['base']; fig, ax = plt.subplots(figsize=(8.5,4))
ax.barh(b.index[::-1], b.values[::-1], color=NAVY)
for i, v in enumerate(b.values[::-1]): ax.text(v+250, i, f'{v:,}', va='center', fontsize=8)
ax.set_xscale('log'); ax.set_xlabel('Patients per year (log scale)')
ax.set_title('Base-case funnel: from malignant CNS tumours to eligible, identified patients', loc='left', fontsize=11)
fig.text(0.01,0.01,'Illustrative model. Several steps are scenarios (see assumptions.csv).', fontsize=7)
fig.tight_layout(rect=(0,0.03,1,1)); fig.savefig(f'{out}/chart_funnel.png', dpi=160); plt.close()

# Chart 2: tornado
s = sens.iloc[::-1]; fig, ax = plt.subplots(figsize=(8.5,3.8))
for i, r in enumerate(s.itertuples()):
    ax.barh(i, r.at_high-ref, left=ref, color=TEAL); ax.barh(i, r.at_low-ref, left=ref, color=RED)
ax.axvline(ref, color='black', lw=0.8); ax.set_yticks(range(len(s))); ax.set_yticklabels([p[:48] for p in s.parameter], fontsize=8)
ax.set_xlabel('Identified and INDIGO-type eligible patients per year'); ax.set_title('Sensitivity: which assumption moves the answer most', loc='left', fontsize=11)
fig.tight_layout(); fig.savefig(f'{out}/chart_tornado.png', dpi=160); plt.close()

# Revenue-style grid (illustrative): patients on therapy x uptake x monthly price
pd.DataFrame([{ 'monthly_price_lakh': p, 'uptake': u, 'annual_value_crore': round(pool['base']*u*p*12/100,1)}
              for p in [0.5,1,2,4] for u in [0.05,0.10,0.20]]).to_csv(f'{out}/price_uptake_grid.csv', index=False)
