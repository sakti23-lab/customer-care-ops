# Customer Care Operations — Data Analysis Portfolio Project

**By:** Moh Nursakti Kamil · [Portfolio](https://portfolio.hirolab.web.id) ·
[Credentials](https://www.credly.com/users/moh-nursakti-kamil)

End-to-end analytics project that demonstrates the skill set a **Customer Care
Data Analyst** owns: extract → model → analyze → visualize → recommend. Built to
support my Google Cloud data/AI certifications (BigQuery, Dataplex, Gemini) and
my pivot from procurement analytics into customer-experience analytics.

## Problem
A travel company's care team lacks visibility into ticket volume, resolution
time, and CSAT by category/segment/channel — so improvement effort is guesswork.

## Pipeline
| Stage | Tool | Artifact |
|-------|------|----------|
| Generate raw tickets (synthetic, travel-themed) | Python | `data/generate_dataset.py` → `data/tickets.csv` |
| Production warehouse + analytics | **BigQuery (SQL)** | `sql/queries.sql` (KPIs, by-category, monthly, FCR-by-channel) |
| Analyze + KPIs + charts | **Python (pandas, matplotlib)** | `analysis/analyze.py` → `outputs/` |
| Dashboard spec | Looker Studio / Tableau | `dashboard/looker_spec.md` |
| Insight narrative | Markdown | `outputs/INSIGHTS.md` |

## Reproduce locally
```bash
cd customer-care-ops
python -m venv .venv && . .venv/bin/activate
pip install pandas matplotlib
python data/generate_dataset.py
python analysis/analyze.py
```
Outputs (KPI CSV, 3 charts, insights) land in `outputs/`.

## Cloud mapping (why this proves the certs)
- **BigQuery / Dataplex** → the analytics layer in `sql/queries.sql` is written
  for a BigQuery warehouse; same logic runs on Dataplex lakehouse.
- **BigQuery ML** → a forecasting follow-up (ticket volume next month) is the
  natural next step and reuses the `Create ML Models with BigQuery ML` badge.
- **Gemini / Vertex AI** → a GenAI follow-up (auto-summarize ticket themes)
  maps to `Develop GenAI Apps with Gemini and Streamlit`.

## Key results (from the synthetic run)
- ~5,800 tickets over 6 months; avg resolution ~17h; FCR <24h ~68%; CSAT 4.0/5.
- Largest category = Booking Change; lowest CSAT = Complaint (clear fix target).
- Full numbers in `outputs/kpi_summary.csv` and `outputs/INSIGHTS.md`.
