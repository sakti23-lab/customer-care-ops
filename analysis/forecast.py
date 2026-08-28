"""Forecast daily customer-care ticket volume (local ARIMA, mirrors BigQuery ML).

Companion to sql/forecast_bqml.sql. The SQL runs ARIMA_PLUS on BigQuery; this
script reproduces the same idea locally with statsmodels so the result is
reproducible without cloud, and emits a forecast chart + MAPE.

Run:  python analysis/forecast.py
Deps: pandas, matplotlib, statsmodels
"""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "outputs")
os.makedirs(OUT, exist_ok=True)

df = pd.read_csv(os.path.join(ROOT, "data", "tickets.csv"), parse_dates=["created_date"])
daily = df.groupby("created_date").size().asfreq("D").fillna(0)
train, test = daily[:-30], daily[-30:]

model = ARIMA(train, order=(2, 1, 2), seasonal_order=(1, 1, 1, 7)).fit()
fc = model.forecast(steps=30)
mape = (abs(test - fc).mean() / test.mean()) * 100

print(f"train={len(train)} days, test={len(test)} days")
print(f"30-day forecast MAPE: {mape:.1f}%")
print(f"Next 7 days volume: {fc.round(0).head(7).astype(int).tolist()}")

plt.figure(figsize=(10, 3.6))
plt.plot(train.index, train.values, label="Actual (train)")
plt.plot(test.index, test.values, label="Actual (test)")
plt.plot(test.index, fc.values, label=f"Forecast (MAPE {mape:.1f}%)", color="red")
plt.title("Daily Ticket Volume — ARIMA Forecast (BigQuery ML style)")
plt.ylabel("Tickets/day"); plt.legend(); plt.tight_layout()
chart = os.path.join(OUT, "chart_forecast.png")
plt.savefig(chart)
print("saved", chart)
