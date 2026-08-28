"""Ticket insight summarizer — GenAI layer (Gemini) with a rule-based fallback.

This module powers app/ticket_insight_app.py. In production it calls the Gemini
API (Google Generative Language) to turn a ticket table into a plain-language
operations brief. Without an API key it falls back to a deterministic,
rule-based summary so the app is always demonstrable.

Proves: Develop GenAI Apps with Gemini and Streamlit (Google Cloud badge).
"""
from __future__ import annotations
import os
import pandas as pd


def _rule_based(df: pd.DataFrame) -> str:
    """Deterministic summary used when no Gemini key is available."""
    resolved = df[df["status"] == "Resolved"].copy()
    total = len(df)
    if resolved.empty:
        return "No resolved tickets to summarize yet."
    by_cat = resolved.groupby("category").agg(
        tickets=("ticket_id", "count"),
        avg_res=("resolution_hours", "mean"),
        csat=("csat_score", "mean"),
    ).sort_values("tickets", ascending=False)
    top = by_cat.index[0]
    worst = by_cat.sort_values("csat").index[0]
    lines = [
        f"Over the period, {total:,} tickets were logged; "
        f"{len(resolved):,} resolved.",
        f"Highest-volume category: {top} ({int(by_cat.loc[top, 'tickets']):,} "
        f"tickets, avg resolution {by_cat.loc[top, 'avg_res']:.1f}h).",
        f"Lowest satisfaction: {worst} (CSAT {by_cat.loc[worst, 'csat']:.2f}, "
        f"avg resolution {by_cat.loc[worst, 'avg_res']:.1f}h) — prioritise this "
        f"for SLA and process fixes.",
        "Recommendation: automate intake for the top category and re-measure "
        "CSAT after a 30-day improvement cycle.",
    ]
    return "\n".join(f"- {l}" for l in lines)


def summarize_tickets(df: pd.DataFrame, api_key: str | None = None) -> str:
    """Return a plain-language operations brief for the ticket table.

    Uses Gemini when `api_key` (or GEMINI_API_KEY env) is set; otherwise the
    rule-based fallback.
    """
    api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return _rule_based(df)

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        resolved = df[df["status"] == "Resolved"]
        sample = resolved.head(200).to_csv(index=False)
        prompt = (
            "You are a customer-care operations analyst. Given the following "
            "ticket sample (CSV), write a tight operations brief: volume driver, "
            "lowest-CSAT category, and one data-driven recommendation. Under 120 "
            "words.\n\n" + sample
        )
        model = genai.GenerativeModel("gemini-2.0-flash")
        resp = model.generate_content(prompt)
        return resp.text
    except Exception as e:  # network/key issue -> graceful fallback
        return _rule_based(df) + f"\n\n[ Gemini call failed ({e}); used fallback ]"
