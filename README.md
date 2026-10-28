# Pharma Commercial Analytics

Two portfolio projects on IDH-mutant glioma in India, built from public data only. Each folder has its own README with the full method, assumptions and limitations.

## 1. [IDH Glioma Funnel Model](IDH_Glioma_Funnel_Model/)
**Question:** How many patients in India each year are IDH-mutant grade 2 glioma, get identified by testing, and fit the INDIGO trial window for vorasidenib?

- Patient funnel from GLOBOCAN incidence to eligible patients, with low/base/high scenarios and a sensitivity (tornado) analysis.
- Base case is about 660 identified, eligible patients a year (range 148 to 3,822).
- Access to IDH testing and the eligibility share drive the result more than tumour biology does.
- Only 4 of 37 public cancer centres confirm both neurosurgery and molecular pathology.
- **Tools:** Python (pandas, matplotlib), Excel inputs

## 2. [IDH Glioma Trial and Competitor Landscape](IDH_Glioma_Trial_Landscape/)
**Question:** Who is developing IDH-targeted therapy for glioma, how mature is each programme, and how visible is India?

- 144 ClinicalTrials.gov studies cleaned into a SQLite database and analysed with 7 SQL queries.
- Vorasidenib has the broadest pipeline (17 trials, 4 in phase 3). Safusidenib is the closest challenger.
- India appears in only 1 of 109 IDH-related trials, and none of the IDH-inhibitor trials lists an Indian site.
- Includes Power BI-ready tables.
- **Tools:** SQL (SQLite), Python, Power BI

## Notes
- All data comes from public sources. No confidential or employer data is used.
- Several inputs are labelled scenarios because no published Indian figure exists. Please read the "Weakest parts of the method" section in each project before quoting any number.
