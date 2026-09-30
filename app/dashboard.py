"""Week 3, Block 4: monitoring dashboard.

Reads logs/agent_runs.jsonl (one line per agent run) and shows the numbers
an operations team would watch.

Run:
    streamlit run app/dashboard.py

TODO (you):
  1. In src/agent/graph.py, append one JSON line per run to logs/agent_runs.jsonl:
     timestamp, intent, confidence, route, escalated, safety_flags, latency_ms.
  2. Run 200 synthetic messages through the agent to create data.
  3. Add: escalation rate over time, intent mix over time (drift),
     p50/p95 latency, and count of each safety flag.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

LOG = Path("logs/agent_runs.jsonl")

st.set_page_config(page_title="MedAssist Monitoring", layout="wide")
st.title("MedAssist monitoring")

if not LOG.exists():
    st.info("No runs logged yet. See the TODO at the top of app/dashboard.py.")
    st.stop()

df = pd.read_json(LOG, lines=True)
c1, c2, c3 = st.columns(3)
c1.metric("Runs", len(df))
c2.metric("Escalation rate", f"{df['escalated'].mean():.1%}")
c3.metric("p95 latency (ms)", int(df["latency_ms"].quantile(0.95)))
st.bar_chart(df["intent"].value_counts())
