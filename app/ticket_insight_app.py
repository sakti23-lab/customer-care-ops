"""Streamlit UI for the GenAI ticket-insight app.

Run locally:
    streamlit run app/ticket_insight_app.py
Upload a tickets CSV (or use the bundled sample) and click "Generate Insight"
to get a Gemini-powered operations brief (falls back to rule-based if no key).

Proves: Develop GenAI Apps with Gemini and Streamlit (Google Cloud badge).
"""
from __future__ import annotations
import os
import pandas as pd
import streamlit as st

from summarize import summarize_tickets

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SAMPLE = os.path.join(ROOT, "data", "tickets.csv")

st.set_page_config(page_title="Care Ops Insight (Gemini)", layout="wide")
st.title("Customer Care — AI Insight Brief")
st.caption("Gemini-powered summarizer (rule-based fallback when no API key)")

src = st.file_uploader("Upload tickets.csv", type="csv")
if src:
    df = pd.read_csv(src, parse_dates=["created_date"])
else:
    if os.path.exists(SAMPLE):
        df = pd.read_csv(SAMPLE, parse_dates=["created_date"])
        st.info("Using bundled sample dataset. Upload your own to override.")
    else:
        st.stop()

st.write(f"**{len(df):,} tickets** loaded.")

if st.button("Generate Insight"):
    with st.spinner("Asking Gemini..."):
        brief = summarize_tickets(df)
    st.markdown("### Operations Brief")
    st.markdown(brief)
