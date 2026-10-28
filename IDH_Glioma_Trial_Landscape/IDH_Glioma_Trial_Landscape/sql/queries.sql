-- Q1: IDH-related trials started per year, with year-over-year change (CTE + LAG)
WITH per_year AS (
  SELECT start_year, COUNT(*) AS trials
  FROM studies
  WHERE idh_related = 1 AND start_year BETWEEN 2012 AND 2026
  GROUP BY start_year
)
SELECT start_year, trials,
       trials - LAG(trials) OVER (ORDER BY start_year) AS change_vs_prev_year
FROM per_year ORDER BY start_year;

-- Q2: Sponsor league table among interventional IDH trials (RANK)
SELECT RANK() OVER (ORDER BY COUNT(*) DESC) AS sponsor_rank,
       sponsor_group AS sponsor, COUNT(*) AS trials,
       SUM(CASE WHEN study_status IN ('RECRUITING','NOT_YET_RECRUITING','ACTIVE_NOT_RECRUITING') THEN 1 ELSE 0 END) AS live_trials
FROM studies
WHERE idh_related = 1 AND study_type = 'INTERVENTIONAL'
GROUP BY sponsor_group
ORDER BY trials DESC, sponsor_group LIMIT 15;

-- Q3: IDH-inhibitor programmes: trials, latest phase and live trials (CTE + RANK)
WITH d AS (
  SELECT dr.drug, s.nct_number, s.phases, s.study_status, s.start_year, s.sponsor
  FROM drugs dr JOIN studies s USING (nct_number)
)
SELECT RANK() OVER (ORDER BY COUNT(*) DESC) AS rnk, drug, COUNT(*) AS trials,
       SUM(CASE WHEN phases LIKE '%PHASE3%' THEN 1 ELSE 0 END) AS phase3_trials,
       SUM(CASE WHEN study_status IN ('RECRUITING','NOT_YET_RECRUITING','ACTIVE_NOT_RECRUITING') THEN 1 ELSE 0 END) AS live_trials,
       MIN(start_year) AS first_start, MAX(start_year) AS latest_start
FROM d GROUP BY drug ORDER BY trials DESC;

-- Q4: Phase mix of interventional IDH trials
SELECT COALESCE(phases,'(not stated)') AS phases, COUNT(*) AS trials
FROM studies WHERE idh_related = 1 AND study_type = 'INTERVENTIONAL'
GROUP BY phases ORDER BY trials DESC;

-- Q5: Where are the sites? Countries ranked by number of distinct IDH trials
SELECT RANK() OVER (ORDER BY COUNT(DISTINCT st.nct_number) DESC) AS rnk,
       st.country, COUNT(DISTINCT st.nct_number) AS trials, COUNT(*) AS sites
FROM sites st JOIN studies s USING (nct_number)
WHERE s.idh_related = 1
GROUP BY st.country ORDER BY trials DESC LIMIT 12;

-- Q6: India footprint (country token must equal 'India', so 'Indiana' is not counted)
SELECT s.nct_number, s.study_title, s.phases, s.study_status, s.sponsor, COUNT(*) AS indian_sites
FROM sites st JOIN studies s USING (nct_number)
WHERE st.country = 'India'
GROUP BY s.nct_number;

-- Q7: Vorasidenib / late-stage pipeline detail
SELECT s.nct_number, dr.drug, s.phases, s.study_status, s.start_year, s.sponsor, s.study_title
FROM drugs dr JOIN studies s USING (nct_number)
WHERE dr.drug IN ('Vorasidenib','Safusidenib') ORDER BY dr.drug, s.start_year;
