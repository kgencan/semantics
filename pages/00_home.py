"""
Home page — live KPIs, problem statement, demo walkthrough, domain registry.
"""

import streamlit as st
import pandas as pd
from data.seed_data import DOMAINS
from utils.kpi import kpi

# ---------------------------------------------------------------------------
# Live counts
# ---------------------------------------------------------------------------
metrics = st.session_state.metrics
recon_log = st.session_state.reconciliation_log

total_metrics = len(metrics)
approved_metrics = sum(1 for m in metrics if m["status"] == "approved")
t1_metrics = sum(1 for m in metrics if m["tier"] == "T1")
open_conflicts = sum(1 for f in recon_log if f["status"] == "open")
semantic_views = sum(1 for m in metrics if m.get("semantic_view_ref"))

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("◈ Semantics")
st.markdown("**Enterprise Semantic Layer Governance Solution**")

# Connection status banner
status_col1, status_col2, status_col3 = st.columns(3)
with status_col1:
    st.markdown("🔘 **Demo mode** · Snowflake: `ANALYTICS` (emulated)")
with status_col2:
    st.markdown("🔧 dbt: last run `2026-03-12 04:31 UTC`")
with status_col3:
    critical_open = sum(1 for f in recon_log if f["status"] == "open" and f["severity"] == "critical")
    if critical_open > 0:
        st.markdown(f"⚠️ **{critical_open} critical** reconciliation findings open")
    else:
        st.markdown(f"✅ No critical findings open")

st.divider()

# ---------------------------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------------------------
critical_count = sum(1 for f in recon_log if f["status"] == "open" and f["severity"] == "critical")
c1, c2, c3, c4, c5 = st.columns(5)
kpi(c1, "Total Metrics",               total_metrics)
kpi(c2, "Approved",                    approved_metrics, f"↑ {round(approved_metrics/total_metrics*100)}% of registry", "#446B5C")
kpi(c3, "T1 (Critical / Regulatory)",  t1_metrics)
kpi(c4, "Open Conflicts",              open_conflicts,   f"↑ {critical_count} critical", "#b91c1c")
kpi(c5, "Semantic Views",              semantic_views,   "↑ live in Snowflake", "#446B5C")

st.divider()

# ---------------------------------------------------------------------------
# Two columns: Problem statement + Demo walkthrough
# ---------------------------------------------------------------------------
left, right = st.columns([3, 2], gap="large")

with left:
    st.subheader("What problem does this solve?")
    st.info(
        """
**Semantic drift** — the same question gets different answers depending on who you ask.

*"What is our loss ratio this quarter?"*

- Claims reports **68%** — using net incurred claims / net earned premium
- Finance reports **74%** — using gross incurred claims / gross written premium

Both teams are right by their own standards. Neither definition is governed, reconciled, or documented. When an AI agent or analyst queries the data warehouse, it gets one of these answers at random.

**Semantics** is the system of record that defines what every metric means, who owns it, and whether it is consistent across domains — before any code is written.
        """
    )

    st.subheader("How it connects to your stack")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Snowflake**")
        st.markdown("""
- Governance metadata in `ANALYTICS.SEMANTIC_GOVERNANCE`
- Semantic views in `ANALYTICS.SEMANTIC_VIEWS`
- Cortex Analyst queries governed definitions
""")
    with col_b:
        st.markdown("**dbt Core**")
        st.markdown("""
- Metrics backed by mart models in `marts/`
- CI/CD syncs dbt metadata → governance tables
- Semantic view YAML co-located with dbt project
""")

with right:
    st.subheader("Demo Walkthrough")
    st.caption("Follow these steps to see Semantics in action.")

    with st.container(border=True):
        st.markdown("**Step 1 — Understand the problem**")
        st.caption("Read the problem statement on the left. This is what happens without a semantic layer.")

    with st.container(border=True):
        st.markdown("**Step 2 — Browse what already exists**")
        st.caption("See the governed metric registry across all 8 domains.")
        if st.button("→ Open Metric Catalog", width="stretch"):
            st.switch_page("pages/01_catalog.py")

    with st.container(border=True):
        st.markdown("**Step 3 — Register a new metric**")
        st.caption("Walk through metric registration. See duplicate detection in action.")
        if st.button("→ Register a Metric", width="stretch", type="primary"):
            st.switch_page("pages/03_new_metric.py")

    with st.container(border=True):
        st.markdown("**Step 4 — See cross-domain conflicts**")
        st.caption("The reconciliation engine found 18 issues. Explore them.")
        if st.button("→ Open Reconciliation Dashboard", width="stretch"):
            st.switch_page("pages/05_reconciliation.py")

    with st.container(border=True):
        st.markdown("**Step 5 — Track to implementation**")
        st.caption("See which metrics have dbt models and Snowflake Semantic Views.")
        if st.button("→ Implementation Tracker", width="stretch"):
            st.switch_page("pages/06_implementation_tracker.py")

# ---------------------------------------------------------------------------
# Domain summary table
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Domain Registry")

domain_rows = []
for d in DOMAINS:
    domain_metrics = [m for m in metrics if m["domain_id"] == d["domain_id"]]
    open_findings = [
        f for f in recon_log
        if (f["domain_a"] == d["domain_name"] or f.get("domain_b") == d["domain_name"])
        and f["status"] == "open"
    ]
    domain_rows.append({
        "Domain": d["domain_name"],
        "Champion": d["champion_name"],
        "Metrics": len(domain_metrics),
        "Approved": sum(1 for m in domain_metrics if m["status"] == "approved"),
        "T1": sum(1 for m in domain_metrics if m["tier"] == "T1"),
        "Open Findings": len(open_findings),
    })

df_domains = pd.DataFrame(domain_rows)
st.dataframe(df_domains, width="stretch", hide_index=True)
