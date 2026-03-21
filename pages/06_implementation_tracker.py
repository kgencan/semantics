"""
F5 — Implementation Tracker
Pipeline view: Registry Only → dbt Model → Snowflake Semantic View.
"""

import streamlit as st
import pandas as pd
from data.seed_data import DOMAINS, METRIC_TECHNICAL_SYNC
from utils.nav import render_sidebar

st.set_page_config(page_title="Implementation Tracker · Semantics", page_icon="◈", layout="wide")

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
render_sidebar()

# ---------------------------------------------------------------------------
# Session state init
# ---------------------------------------------------------------------------
if "metrics" not in st.session_state:
    from data.seed_data import METRICS
    st.session_state.metrics = [dict(m) for m in METRICS]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
DOMAIN_MAP = {d["domain_id"]: d["domain_name"] for d in DOMAINS}

def get_stage(m):
    sync = METRIC_TECHNICAL_SYNC.get(m["metric_id"])
    if m.get("semantic_view_ref") or (sync and sync.get("semantic_view_ref")):
        return "Semantic View"
    if m.get("has_dbt_model") or (sync and sync.get("dbt_model_path")):
        return "dbt Model"
    return "Registry Only"

STAGE_ICON = {
    "Semantic View": "✨",
    "dbt Model": "🔧",
    "Registry Only": "📋",
}

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("🔧 Implementation Tracker")
st.caption("Track every metric from registry to dbt model to Snowflake Semantic View.")

# Sync status bar
sync_col1, sync_col2, _ = st.columns([2, 2, 6])
with sync_col1:
    st.caption("Last dbt sync: `2026-03-12 04:31:07 UTC`")
with sync_col2:
    st.button(
        "↻ Sync from dbt",
        disabled=True,
        help="Requires active Snowflake + dbt Cloud connection. In production, triggers a CI/CD run that syncs dbt metadata into the governance registry.",
        use_container_width=False,
    )

st.divider()

# ---------------------------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------------------------
metrics = st.session_state.metrics
stages = [get_stage(m) for m in metrics]

sv_count = stages.count("Semantic View")
dbt_count = stages.count("dbt Model")
reg_count = stages.count("Registry Only")

total = len(metrics)
approved_t1t2 = [m for m in metrics if m["status"] == "approved" and m["tier"] in ("T1", "T2")]
approved_implemented = [m for m in approved_t1t2 if get_stage(m) in ("dbt Model", "Semantic View")]
coverage_pct = len(approved_implemented) / len(approved_t1t2) if approved_t1t2 else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("✨ Semantic View", sv_count, delta=f"{round(sv_count/total*100)}% of registry")
c2.metric("🔧 dbt Model", dbt_count, delta=f"{round(dbt_count/total*100)}% of registry")
c3.metric("📋 Registry Only", reg_count, delta=f"{round(reg_count/total*100)}% of registry")
c4.metric("T1/T2 Approved Coverage", f"{round(coverage_pct*100)}%", delta=f"{len(approved_implemented)}/{len(approved_t1t2)} metrics")

# Overall progress bar
st.markdown("**Approved T1 + T2 Metrics — Implementation Progress**")
st.progress(coverage_pct, text=f"{len(approved_implemented)} of {len(approved_t1t2)} approved operational/critical metrics have a dbt model or Semantic View")

st.divider()

# ---------------------------------------------------------------------------
# Pipeline visualization
# ---------------------------------------------------------------------------
st.markdown("**Implementation Pipeline**")

pipeline_data = {"Stage": ["📋 Registry Only", "🔧 dbt Model", "✨ Semantic View"], "Count": [reg_count, dbt_count, sv_count]}
pipeline_df = pd.DataFrame(pipeline_data)
st.bar_chart(pipeline_df.set_index("Stage"), height=150, horizontal=True)

st.divider()

# ---------------------------------------------------------------------------
# Per-domain breakdown
# ---------------------------------------------------------------------------
st.subheader("By Domain")

for domain in DOMAINS:
    domain_metrics = [m for m in metrics if m["domain_id"] == domain["domain_id"]]
    if not domain_metrics:
        continue

    domain_stages = [get_stage(m) for m in domain_metrics]
    d_sv = domain_stages.count("Semantic View")
    d_dbt = domain_stages.count("dbt Model")
    d_reg = domain_stages.count("Registry Only")

    d_approved_t1t2 = [m for m in domain_metrics if m["status"] == "approved" and m["tier"] in ("T1", "T2")]
    d_coverage = sum(1 for m in d_approved_t1t2 if get_stage(m) in ("dbt Model", "Semantic View")) / len(d_approved_t1t2) if d_approved_t1t2 else 0

    has_gaps = any(
        m["status"] == "approved" and m["tier"] == "T1" and get_stage(m) == "Registry Only"
        for m in domain_metrics
    )

    expander_label = f"{domain['domain_name']} — {len(domain_metrics)} metrics"
    if has_gaps:
        expander_label += " ⚠️"

    with st.expander(expander_label, expanded=has_gaps):
        prog_col, stats_col = st.columns([3, 1])
        with prog_col:
            st.progress(d_coverage, text=f"{round(d_coverage*100)}% T1/T2 approved metrics implemented")
        with stats_col:
            st.markdown(f"✨ {d_sv} · 🔧 {d_dbt} · 📋 {d_reg}")

        # Metrics table
        rows = []
        for m in sorted(domain_metrics, key=lambda x: ({"T1": 0, "T2": 1, "T3": 2}.get(x["tier"], 9), x["display_name"])):
            stage = get_stage(m)
            stage_icon = STAGE_ICON.get(stage, "")
            tier_icon = {"T1": "🔴", "T2": "🟠", "T3": "⚫"}.get(m["tier"], "")
            status_icon = {"approved": "✅", "under_review": "🔵", "draft": "⚪", "deprecated": "❌"}.get(m["status"], "")

            sync = METRIC_TECHNICAL_SYNC.get(m["metric_id"])
            dbt_path = sync["dbt_model_path"] if sync else "—"
            sv_ref = (sync.get("semantic_view_ref") if sync else None) or m.get("semantic_view_ref") or "—"
            tests = "✅" if sync and sync.get("dbt_tests_passing") else ("❌" if sync and sync.get("dbt_tests_passing") is False else "—")

            # Flag implementation gap
            gap_flag = ""
            if m["status"] == "approved" and m["tier"] == "T1" and stage == "Registry Only":
                gap_flag = " ⚠️"

            rows.append({
                "Metric": m["display_name"] + gap_flag,
                "ID": m["metric_id"],
                "Tier": f"{tier_icon} {m['tier']}",
                "Status": f"{status_icon} {m['status'].replace('_', ' ').title()}",
                "Stage": f"{stage_icon} {stage}",
                "dbt Model Path": dbt_path,
                "Semantic View": sv_ref if sv_ref != "—" else "—",
                "Tests": tests,
            })

        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # Gap warnings
        gaps = [m for m in domain_metrics if m["status"] == "approved" and m["tier"] == "T1" and get_stage(m) == "Registry Only"]
        for g in gaps:
            st.warning(
                f"⚠️ **Implementation gap:** `{g['metric_id']}` **{g['display_name']}** is approved T1 but has no dbt model.  \n"
                f"This metric cannot be queried by Cortex Analyst or served in Snowflake Semantic Views."
            )
