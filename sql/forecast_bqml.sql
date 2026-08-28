-- Customer Care Ops — Forecasting (BigQuery ML / ARIMA_PLUS)
-- Companion to analysis/forecast.ipynb. Demonstrates the "Create ML Models with
-- BigQuery ML" badge on real ticket-volume data.
--
-- 1) Daily ticket volume (training table from tickets_raw)
CREATE OR REPLACE TABLE `<project>.<dataset>.ticket_volume_daily` AS
SELECT
  created_date AS ds,
  COUNT(*)      AS y
FROM `<project>.<dataset>.tickets_raw`
GROUP BY created_date;

-- 2) Train an ARIMA_PLUS model (handles seasonality + holidays automatically)
CREATE OR REPLACE MODEL `<project>.<dataset>.ticket_volume_forecast`
OPTIONS(
  model_type           = 'ARIMA_PLUS',
  time_series_timestamp_col = 'ds',
  time_series_data_col     = 'y',
  time_series_freq         = 'DAY',
  forecast_limit           = 30,
  data_frequency           = 'AUTO_FREQUENCY'
) AS
SELECT ds, y FROM `<project>.<dataset>.ticket_volume_daily`;

-- 3) Forecast the next 30 days
SELECT *
FROM ML.FORECAST(
  MODEL `<project>.<dataset>.ticket_volume_forecast`,
  STRUCT(30 AS horizon)
);

-- 4) (Optional) accuracy check on a holdout — MAPE
-- Evaluate via ML.EVALUATE on the same model for in-sample fit diagnostics.
SELECT *
FROM ML.EVALUATE(
  MODEL `<project>.<dataset>.ticket_volume_forecast`
);
