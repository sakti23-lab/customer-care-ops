"""Customer-care operational analysis (Pandas) for the portfolio project.

Reads data/tickets.csv, computes the KPIs a Customer Care Data Analyst owns
(volume, resolution time, CSAT, first-contact resolution, segmentation), and
emits: a KPI summary CSV, three charts, and an INSIGHTS.md narrative.

Run:  python analysis/analyze.py
Deps: pandas, matplotlib  (uv: uv pip install pandas matplotlib)
"""
import os
import sys
import datetime as dt

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
DATA = os.path.join(ROOT, "data", "tickets.csv")
OUT  = os.path.join(ROOT, "outputs")
os.makedirs(OUT, exist_ok=True)

# ensure data exists
if not os.path.exists(DATA):
    sys.path.insert(0, os.path.join(ROOT, "data"))
    from generate_dataset import generate
    generate(DATA)

df = pd.read_csv(DATA, parse_dates=["created_date"])
df["month"] = df["created_date"].dt.to_period("M").astype(str)
df["csat_score"] = pd.to_numeric(df["csat_score"], errors="coerce")
df["resolution_hours"] = pd.to_numeric(df["resolution_hours"], errors="coerce")

# ---------- KPIs ----------
total = len(df)
resolved = df[df["status"] == "Resolved"]
fcr = resolved["resolution_hours"].le(24).mean()           # resolved within 24h
avg_res = resolved["resolution_hours"].mean()
avg_csat = resolved["csat_score"].mean()
csat_top2 = resolved["csat_score"].ge(4).mean()

kpi = {
    "Total tickets": total,
    "Resolved": len(resolved),
    "Open": int((df["status"] == "Open").sum()),
    "Avg resolution (hrs)": round(avg_res, 1),
    "First-contact resolution (<24h)": f"{fcr*100:.1f}%",
    "Avg CSAT (1-5)": round(avg_csat, 2),
    "Top-2 box CSAT (>=4)": f"{csat_top2*100:.1f}%",
}
kpi_df = pd.DataFrame(list(kpi.items()), columns=["Metric", "Value"])
kpi_df.to_csv(os.path.join(OUT, "kpi_summary.csv"), index=False)

# by category
by_cat = resolved.groupby("category").agg(
    tickets=("ticket_id", "count"),
    avg_res_hrs=("resolution_hours", "mean"),
    avg_csat=("csat_score", "mean"),
).sort_values("tickets", ascending=False)
by_cat["avg_res_hrs"] = by_cat["avg_res_hrs"].round(1)
by_cat["avg_csat"] = by_cat["avg_csat"].round(2)
by_cat.to_csv(os.path.join(OUT, "by_category.csv"))

# by segment
by_seg = resolved.groupby("customer_segment").agg(
    tickets=("ticket_id", "count"),
    avg_csat=("csat_score", "mean"),
).round(2).sort_values("tickets", ascending=False)
by_seg.to_csv(os.path.join(OUT, "by_segment.csv"))

# monthly volume
monthly = df.groupby("month").size()

# ---------- charts ----------
plt.rcParams.update({"figure.dpi": 110, "font.size": 9})

# 1) monthly volume stacked by category
piv = df.pivot_table(index="month", columns="category",
                     values="ticket_id", aggfunc="count", fill_value=0)
piv.plot(kind="bar", stacked=True, figsize=(8, 3.6))
plt.title("Monthly Ticket Volume by Category")
plt.ylabel("Tickets"); plt.xlabel(""); plt.tight_layout()
plt.savefig(os.path.join(OUT, "chart_volume.png")); plt.close()

# 2) avg resolution + CSAT by category
fig, ax1 = plt.subplots(figsize=(13, 4.6))
cats = by_cat.index.tolist()
ax1.bar(cats, by_cat["avg_res_hrs"], color="#4C9F70")
ax1.set_ylabel("Avg resolution (hrs)", color="#4C9F70")
ax2 = ax1.twinx()
ax2.plot(cats, by_cat["avg_csat"], color="#C0392B", marker="o")
ax2.set_ylabel("Avg CSAT", color="#C0392B"); ax2.set_ylim(0, 5.5)
plt.title("Resolution Time vs CSAT by Category")
plt.xticks(rotation=40, ha="right", fontsize=8)
fig.subplots_adjust(left=0.07, right=0.91, bottom=0.33, top=0.90)
plt.savefig(os.path.join(OUT, "chart_res_csat.png")); plt.close()

# 3) CSAT by segment
by_seg["avg_csat"].plot(kind="bar", figsize=(6, 3.2), color="#2E86C1")
plt.title("Average CSAT by Customer Segment")
plt.ylabel("Avg CSAT"); plt.xticks(rotation=20, ha="right")
plt.tight_layout(); plt.savefig(os.path.join(OUT, "chart_segment.png")); plt.close()

# ---------- insights ----------
worst = by_cat.sort_values("avg_csat").index[0]
worst_res = by_cat.loc[worst]
top_vol = by_cat.index[0]
insights = f"""# Insights — Customer Care Operations

*Generated {dt.date.today().isoformat()} from a synthetic travel-themed ticket set ({total:,} tickets, {df['created_date'].min().date()} to {df['created_date'].max().date()}).*

## Headline KPIs
- **{total:,} tickets** handled; **{kpi['Open']}** still open.
- Average resolution time **{avg_res:.1f} hrs**; first-contact resolution (<24h) **{fcr*100:.1f}%**.
- Average CSAT **{avg_csat:.2f}/5**, top-2-box **{csat_top2*100:.1f}%**.

## What the data says
1. **Volume driver:** `{top_vol}` is the largest category ({int(by_cat.loc[top_vol,'tickets']):,} tickets) — and a prime candidate for self-service deflection.
2. **Experience gap:** `{worst}` shows the lowest CSAT ({worst_res['avg_csat']:.2f}) with avg resolution {worst_res['avg_res_hrs']:.1f}h — the clearest improvement target.
3. **Segment signal:** `{by_seg.index[0]}` travellers are the highest-volume segment; their CSAT ({by_seg.iloc[0]['avg_csat']:.2f}) is the benchmark to protect.

## Recommended actions (data-driven)
- Automate `{top_vol}` intake (App/WhatsApp) to lift first-contact resolution above {fcr*100+5:.0f}%.
- Stand up an SLA on `{worst}` at <{worst_res['avg_res_hrs']*0.7:.0f}h and re-measure CSAT after 30 days.
- Track these KPIs live in a Looker Studio / Tableau dashboard (see dashboard/looker_spec.md).
"""
with open(os.path.join(OUT, "INSIGHTS.md"), "w") as f:
    f.write(insights)

print("KPI summary:\n", kpi_df.to_string(index=False))
print("\nby category:\n", by_cat.to_string())
print("\nOutputs written to:", OUT)
