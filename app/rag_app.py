"""Streamlit UI for the Customer-Care RAG chatbot.

Run:  streamlit run app/rag_app.py
Needs: data/knowledge_base.csv + app/rag.py

Proves the RAG pattern (retrieve -> ground -> generate) with Gemini; falls back
to a local TF-IDF retriever when no API key is set.
"""
from __future__ import annotations
import os
import streamlit as st

from rag import RAGEngine

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
KB = os.path.join(ROOT, "data", "knowledge_base.csv")

st.set_page_config(page_title="Care RAG Assistant", layout="wide")
st.title("Customer Care — RAG Assistant")
st.caption("Retrieval-Augmented Generation over the support knowledge base "
           "(Gemini when API key set; local retriever otherwise)")

if "engine" not in st.session_state:
    st.session_state.engine = RAGEngine(KB)
if "log" not in st.session_state:
    st.session_state.log = []

with st.sidebar:
    st.write(f"Mode: **{st.session_state.engine.mode.upper()}**")
    st.write(f"Knowledge base: **{len(st.session_state.engine.docs)} entries**")
    st.write("Ask about refunds, baggage, delays, booking changes, loyalty.")

q = st.chat_input("Tanya layanan pelanggan...")
if q:
    ans = st.session_state.engine.answer(q)
    st.session_state.log.append(("user", q))
    st.session_state.log.append(("assistant", ans))

for role, msg in st.session_state.log:
    with st.chat_message(role):
        st.markdown(msg)
