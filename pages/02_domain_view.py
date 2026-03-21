"""
F2 — Domain View
Per-domain dashboard: champion info, metric breakdown, implementation coverage, findings.
"""

import streamlit as st
import pandas as pd
from data.seed_data import DOMAINS, METRIC_TECHNICAL_SYNC
from utils.nav import render_sidebar

st.set_page_config(page_title="Domain View · Semantics", page_icon="◈", layout="wide")

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
if "reconciliation_log" not in st.session_state:
    from data.seed_data import RECONCILIATION_LOG
    st.session_state.reconciliation_log = [dict(f) for f in RECONCILIATION_LOG]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
DOMAIN_MAP = {d["domain_id"]: d["domain_name"] for d in DOMAINS}

def get_implementation_stage(m):
    sync = METRIC_TECHNICAL_SYNC.get(m["metric_id"])
    if sync and sync.get("semantic_view_ref"):
        return "Semantic View"
    if m.get("has_dbt_model") or (sync and sync.get("dbt_model_path")):
        return "dbt Model"
    return "Registry Only"

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("🏛 Domain View")
st.caption("Per-domain dashboard — metrics, ownership, implementation coverage, and reconciliation findings.")

# ---------------------------------------------------------------------------
# Domain tabs
# ---------------------------------------------------------------------------
tab_labels = [d["domain_name"] for d in DOMAINS]
tabs = st.tabs(tab_labels)

for tab, domain in zip(tabs, DOMAINS):
    with tab:
        domain_metrics = [m for m in st.session_state.metrics if m["domain_id"] == domain["domain_id"]]
        recon_findings = [
            f for f in st.session_state.reconciliation_log
            if f["domain_a"] == domain["domain_name"] or f.get("domain_b") == domain["domain_name"]
        ]
        open_findings = [f for f in recon_findings if f["status"] == "open"]
        critical_findings = [f for f in open_findings if f["severity"] == "critical"]

        # ── Summary metrics ────────────────────────────────────────────────
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Total Metrics", len(domain_metrics))
        m2.metric("Approved", sum(1 for m in domain_metrics if m["status"] == "approved"))
        m3.metric("Under Review", sum(1 for m in domain_metrics if m["status"] == "under_review"))
        m4.metric("Open Findings", len(open_findings), delta=f"{len(critical_findings)} critical" if critical_findings else None, delta_color="inverse" if critical_findings else "off")
        m5.metric("Draft / Exploratory", sum(1 for m in domain_metrics if m["status"] == "draft"))

        st.divider()

        # ── Two-column layout ──────────────────────────────────────────────
        left_col, right_col = st.columns([3, 2], gap="large")

        with left_col:
            # Champion info
            with st.container(border=True):
                st.markdown(f"**Domain Champion**")
                st.markdown(f"### {domain['champion_name']}")
                st.caption(f"{domain['champion_role']}")
                st.caption(f"📧 {domain['champion_email']}")
                st.caption(f"Domain tier: **{domain['tier']}**")

            st.markdown(f"**About this domain**")
            st.write(domain["description"])

        with right_col:
            # Implementation coverage
            if domain_metrics:
                stages = [get_implementation_stage(m) for m in domain_metrics]
                sv_count = stages.count("Semantic View")
                dbt_count = stages.count("dbt Model")
                reg_count = stages.count("Registry Only")

                implemented = sv_count + dbt_count
                coverage_pct = implemented / len(domain_metrics)

                st.markdown("**Implementation Coverage**")
                st.progress(coverage_pct, text=f"{round(coverage_pct * 100)}% have dbt model or Semantic View")
                col_s1, col_s2, col_s3 = st.columns(3)
                col_s1.metric("Semantic View", sv_count)
                col_s2.metric("dbt Model", dbt_count)
                col_s3.metric("Registry Only", reg_count)

                # Tier breakdown
                st.markdown("**Tier Breakdown**")
                t1 = sum(1 for m in domain_metrics if m["tier"] == "T1")
                t2 = sum(1 for m in domain_metrics if m["tier"] == "T2")
                t3 = sum(1 for m in domain_metrics if m["tier"] == "T3")
                tier_df = pd.DataFrame({"Tier": ["T1", "T2", "T3"], "Count": [t1, t2, t3]})
                st.bar_chart(tier_df.set_index("Tier"), height=150)

        st.divider()

        # ── Metrics table ──────────────────────────────────────────────────
        st.markdown(f"**Metrics in {domain['domain_name']}**")

        if domain_metrics:
            rows = []
            for m in sorted(domain_metrics, key=lambda x: (x["tier"], x["display_name"])):
                tier_icon = {"T1": "🔴", "T2": "🟠", "T3": "⚫"}.get(m["tier"], "")
                status_icon = {"approved": "✅", "under_review": "🔵", "draft": "⚪", "deprecated": "❌"}.get(m["status"], "")
                rows.append({
                    "ID": m["metric_id"],
                    "Metric": m["display_name"],
                    "Tier": f"{tier_icon} {m['tier']}",
                    "Type": m["metric_type"].title(),
                    "Status": f"{status_icon} {m['status'].replace('_', ' ').title()}",
                    "Stage": get_implementation_stage(m),
                    "Owner": m["owner_name"],
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.caption("No metrics registered for this domain.")

        # ── Reconciliation findings ────────────────────────────────────────
        if open_findings:
            st.divider()
            st.markdown(f"**Open Reconciliation Findings ({len(open_findings)})**")
            sev_order = {"critical": 0, "warning": 1, "info": 2}
            for f in sorted(open_findings, key=lambda x: sev_order.get(x["severity"], 9)):
                sev_icon = {"critical": "🔴", "warning": "🟠", "info": "🔵"}.get(f["severity"], "")
                type_label = {"contradiction": "Contradiction", "duplicate": "Duplicate", "overlap": "Overlap", "gap": "Gap", "suggestion": "Suggestion"}.get(f["finding_type"], f["finding_type"].title())
                domain_pair = f["domain_a"] + (f" ↔ {f['domain_b']}" if f.get("domain_b") else "")
                # Truncate description
                desc_short = (f.get("description") or "")[:200]
                if len(f.get("description", "")) > 200:
                    desc_short += "…"
                with st.container(border=True):
                    st.markdown(f"{sev_icon} **{f['finding_id']}** · {type_label} · {domain_pair}")
                    st.caption(desc_short)
                    if st.button("View in Reconciliation →", key=f"goto_recon_{f['finding_id']}_{domain['domain_id']}"):
                        st.switch_page("pages/05_reconciliation.py")
