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

## Project 2 — Ticket Volume Forecasting (BigQuery ML)
Predicts next-30-day ticket volume so the care team can staff ahead. The
**production model is ARIMA_PLUS on BigQuery** (`sql/forecast_bqml.sql`, proving
the *Create ML Models with BigQuery ML* badge); a local `statsmodels` replica
(`analysis/forecast.py`) reproduces it for reproducibility.

- **Result (local replica):** 30-day forecast **MAPE 11.7%**; next-7-day volume
  ≈ 28–37 tickets/day (weekend peaks). Chart: `outputs/chart_forecast.png`.
- **Cloud mapping:** same `ARIMA_PLUS` query runs unchanged on BigQuery against
  `ticket_volume_daily`; `ML.EVALUATE` returns in-sample fit diagnostics.

## Project 3 — GenAI Ticket Insight (Gemini + Streamlit)
Turns the ticket table into a plain-language operations brief with **Gemini**
(`app/summarize.py` + `app/ticket_insight_app.py`). Proves the
*Develop GenAI Apps with Gemini and Streamlit* badge. It **gracefully falls
back** to a deterministic rule-based summary when no API key is present, so the
app is always demonstrable (verified: produced a correct brief on 5,305 tickets).

- Run: `pip install -r app/requirements.txt && streamlit run app/ticket_insight_app.py`
- **Why it matters:** maps directly to the Trinusa JD — "explore how LLM
  applications can enhance the efficiency of customer care."

## Project 4 — Customer-Care RAG Assistant (Gemini + Vector retrieval)
A **Retrieval-Augmented Generation** chatbot over the support knowledge base
(`data/knowledge_base.csv`). It retrieves the most relevant FAQ entries
(local TF-IDF, or Gemini `text-embedding-004` when a key is set) and grounds the
answer in them — the same pattern as **Vertex AI Vector Search + Gemini** in
production. Proves the *Engineer AI Agents with ADK / Gemini Enterprise* badges.

- Run: `streamlit run app/rag_app.py` (set `GEMINI_API_KEY` for live generative answers)
- **Why it matters:** demonstrates an end-to-end LLM product (retrieve → ground →
  generate) — the strongest signal of applied AI skill for a data/AI role.

## Reproduce locally
```bash
cd customer-care-ops
python -m venv .venv && . .venv/bin/activate
pip install pandas matplotlib statsmodels numpy streamlit google-generativeai
python data/generate_dataset.py
python analysis/analyze.py
python analysis/forecast.py
# optional demos:
#   streamlit run app/ticket_insight_app.py
#   streamlit run app/rag_app.py
```
Outputs (KPI CSV, 3 charts, insights) land in `outputs/`.

## Cloud mapping (why this proves the certs)
- **BigQuery / Dataplex** → the analytics layer in `sql/queries.sql` is written
  for a BigQuery warehouse; same logic runs on Dataplex lakehouse.
- **BigQuery ML** → a forecasting follow-up (ticket volume next month) is the
  natural next step and reuses the `Create ML Models with BigQuery ML` badge.
- **Gemini / Vertex AI** → a GenAI follow-up (auto-summarize ticket themes)
  maps to `Develop GenAI Apps with Gemini and Streamlit`.

## Deploy the demos (Streamlit Community Cloud — free, public URL)
1. Go to https://share.streamlit.io and **Sign in with GitHub** (`sakti23-lab`).
2. Click **New app** → select repo `sakti23-lab/customer-care-ops`, branch `master`.
3. **Main file path**: `app/rag_app.py` (RAG Assistant) or `app/ticket_insight_app.py`
   (ticket insight). Click **Deploy**.
4. After deploy, open **App settings (⋯) → Secrets** and paste:
   ```toml
   GEMINI_API_KEY = "YOUR_GEMINI_KEY"
   ```
   Streamlit injects this as an environment variable, which `rag.py` /
   `summarize.py` already read via `os.environ.get("GEMINI_API_KEY")`.
   With a key the apps switch from the local fallback to **live Gemini**
   (`text-embedding-004` for RAG retrieval, `gemini-2.0-flash` for generation).
5. Share the resulting `https://xxx.streamlit.app` URL in your CV / portfolio.

Without a key the apps still run (local fallback), so the demo is always live.

## Key results (from the synthetic run)
- ~5,800 tickets over 6 months; avg resolution ~17h; FCR <24h ~68%; CSAT 4.0/5.
- Largest category = Booking Change; lowest CSAT = Complaint (clear fix target).
- Full numbers in `outputs/kpi_summary.csv` and `outputs/INSIGHTS.md`.
