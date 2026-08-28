-- Customer Care Ops — production pipeline (BigQuery)
-- Stage 1: raw tickets land in <dataset>.tickets_raw (e.g. via Cloud Storage / API).
-- This file shows the analytics layer a Customer Care Data Analyst would own.

-- 1) KPI summary (last 6 months)
SELECT
  COUNT(*)                                             AS total_tickets,
  COUNTIF(status = 'Resolved')                         AS resolved,
  COUNTIF(status = 'Open')                             AS open_tickets,
  ROUND(AVG(IF(status='Resolved', resolution_hours, NULL)), 1) AS avg_resolution_hrs,
  ROUND(AVG(IF(status='Resolved', csat_score, NULL)), 2)       AS avg_csat,
  ROUND(100 * AVG(IF(status='Resolved' AND resolution_hours <= 24, 1, 0)), 1) AS fcr_pct_24h,
  ROUND(100 * AVG(IF(status='Resolved' AND csat_score >= 4, 1, 0)), 1)        AS top2box_csat_pct
FROM `<project>.<dataset>.tickets_raw`;

-- 2) Volume + CSAT by category (improvement targeting)
SELECT
  category,
  COUNT(*)                                   AS tickets,
  ROUND(AVG(resolution_hours), 1)            AS avg_res_hrs,
  ROUND(AVG(csat_score), 2)                   AS avg_csat
FROM `<project>.<dataset>.tickets_raw`
WHERE status = 'Resolved'
GROUP BY category
ORDER BY tickets DESC;

-- 3) Monthly trend for dashboard time-series
SELECT
  FORMAT_DATE('%Y-%m', created_date)         AS month,
  category,
  COUNT(*)                                   AS tickets,
  ROUND(AVG(csat_score), 2)                  AS avg_csat
FROM `<project>.<dataset>.tickets_raw`
WHERE status = 'Resolved'
GROUP BY month, category
ORDER BY month;

-- 4) First-contact resolution by channel (deflection opportunity)
SELECT
  channel,
  COUNT(*)                                              AS tickets,
  ROUND(100 * AVG(IF(resolution_hours <= 24, 1, 0)), 1) AS fcr_pct
FROM `<project>.<dataset>.tickets_raw`
WHERE status = 'Resolved'
GROUP BY channel
ORDER BY tickets DESC;
