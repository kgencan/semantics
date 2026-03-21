"""
Semantics — Enterprise Semantic Layer Governance Platform
Home page & session state initialisation.
"""

import streamlit as st
from data.seed_data import METRICS, RECONCILIATION_LOG, DOMAINS
from utils.nav import render_sidebar

st.set_page_config(
    page_title="Semantics",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Session state — initialise all mutable state on first load
# ---------------------------------------------------------------------------
if "metrics" not in st.session_state:
    st.session_state.metrics = [dict(m) for m in METRICS]
if "change_requests" not in st.session_state:
    st.session_state.change_requests = []
if "reconciliation_log" not in st.session_state:
    st.session_state.reconciliation_log = [dict(f) for f in RECONCILIATION_LOG]
if "selected_metric_id" not in st.session_state:
    st.session_state.selected_metric_id = None
if "selected_domain_id" not in st.session_state:
    st.session_state.selected_domain_id = None
if "cr_prefill_domain" not in st.session_state:
    st.session_state.cr_prefill_domain = None
if "cr_prefill_title" not in st.session_state:
    st.session_state.cr_prefill_title = None
if "cr_prefill_description" not in st.session_state:
    st.session_state.cr_prefill_description = None
if "demo_step" not in st.session_state:
    st.session_state.demo_step = None

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
render_sidebar()

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
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Metrics", total_metrics)
c2.metric("Approved", approved_metrics, delta=f"{round(approved_metrics/total_metrics*100)}% of registry")
c3.metric("T1 (Critical / Regulatory)", t1_metrics)
c4.metric("Open Conflicts", open_conflicts, delta=f"{sum(1 for f in recon_log if f['status']=='open' and f['severity']=='critical')} critical", delta_color="inverse")
c5.metric("Semantic Views", semantic_views, delta="live in Snowflake")

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
        if st.button("→ Open Metric Catalog", use_container_width=True):
            st.switch_page("pages/01_catalog.py")

    with st.container(border=True):
        st.markdown("**Step 3 — Register a new metric**")
        st.caption("Walk through metric registration. See duplicate detection in action.")
        if st.button("→ Register a Metric", use_container_width=True, type="primary"):
            st.switch_page("pages/03_new_metric.py")

    with st.container(border=True):
        st.markdown("**Step 4 — See cross-domain conflicts**")
        st.caption("The reconciliation engine found 18 issues. Explore them.")
        if st.button("→ Open Reconciliation Dashboard", use_container_width=True):
            st.switch_page("pages/05_reconciliation.py")

    with st.container(border=True):
        st.markdown("**Step 5 — Track to implementation**")
        st.caption("See which metrics have dbt models and Snowflake Semantic Views.")
        if st.button("→ Implementation Tracker", use_container_width=True):
            st.switch_page("pages/06_implementation_tracker.py")

# ---------------------------------------------------------------------------
# Domain summary table
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Domain Registry")

import pandas as pd

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
st.dataframe(df_domains, use_container_width=True, hide_index=True)
