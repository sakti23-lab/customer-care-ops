# Dashboard Spec — Customer Care Ops (Looker Studio / Tableau Public)

Goal: a single screen a Care Ops lead checks daily. Driven by `sql/queries.sql`
against BigQuery.

## Tiles
1. **KPI strip** (top): Total tickets, Open, Avg resolution (hrs), FCR <24h %,
   Avg CSAT, Top-2-box CSAT %. Source: query #1.
2. **Monthly volume by category** (stacked bar). Source: query #3.
3. **Resolution time vs CSAT by category** (combo: bars = hrs, line = CSAT).
   Source: query #2. Surfaces the worst-experience category.
4. **FCR % by channel** (bar). Source: query #4. Shows best deflection channel.
5. **CSAT trend** (line over month). Source: query #3.

## Filters
- Date range, Region, Customer segment, Channel.

## Why this matters for the role
Mirrors the Trinusa Data Analyst JD: "develop and maintain dashboards that track
critical Goals related to customer care operations, performance, and customer
experience" + "identify trends, customer segmentation, key drivers."
