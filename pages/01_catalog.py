"""
F1 — Metric Catalog
Searchable, filterable registry of all governed metrics.
"""

import streamlit as st
import pandas as pd
from data.seed_data import DOMAINS, DIMENSIONS, METRIC_DIMENSIONS, METRIC_TAGS, METRIC_DEPENDENCIES, METRIC_DICTIONARY_LINKS, METRIC_TECHNICAL_SYNC


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
DOMAIN_MAP = {d["domain_id"]: d["domain_name"] for d in DOMAINS}
TIER_COLORS = {"T1": "🔴", "T2": "🟠", "T3": "⚫"}
STATUS_COLORS = {
    "approved": "✅",
    "under_review": "🔵",
    "draft": "⚪",
    "deprecated": "❌",
}

def tier_label(tier):
    return f"{TIER_COLORS.get(tier, '')} {tier}"

def status_label(status):
    return f"{STATUS_COLORS.get(status, '')} {status.replace('_', ' ').title()}"

# ---------------------------------------------------------------------------
# Session state init
# ---------------------------------------------------------------------------
if "metrics" not in st.session_state:
    from data.seed_data import METRICS
    st.session_state.metrics = [dict(m) for m in METRICS]

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.markdown("# :material/table_chart: Metric Catalog")
st.caption(f"{len(st.session_state.metrics)} metrics registered across {len(DOMAINS)} domains")

# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------
f1, f2, f3, f4, f5 = st.columns([2, 1, 1, 1, 2])

with f1:
    domain_options = ["All domains"] + [d["domain_name"] for d in DOMAINS]
    filter_domain = st.selectbox("Domain", domain_options, placeholder="All domains")

with f2:
    filter_tier = st.multiselect("Tier", ["T1", "T2", "T3"], placeholder="All tiers")

with f3:
    filter_status = st.multiselect(
        "Status",
        ["approved", "under_review", "draft", "deprecated"],
        placeholder="All statuses",
        format_func=lambda s: s.replace("_", " ").title(),
    )

with f4:
    filter_type = st.multiselect(
        "Type",
        ["KPI", "operational", "financial", "actuarial", "regulatory", "derived"],
        placeholder="All types",
    )

with f5:
    free_text = st.text_input("Search", placeholder="Search metrics…")

# ---------------------------------------------------------------------------
# Apply filters
# ---------------------------------------------------------------------------
metrics = st.session_state.metrics

if filter_domain and filter_domain != "All domains":
    domain_id = next((d["domain_id"] for d in DOMAINS if d["domain_name"] == filter_domain), None)
    metrics = [m for m in metrics if m["domain_id"] == domain_id]

if filter_tier:
    metrics = [m for m in metrics if m["tier"] in filter_tier]

if filter_status:
    metrics = [m for m in metrics if m["status"] in filter_status]

if filter_type:
    metrics = [m for m in metrics if m["metric_type"] in filter_type]

if free_text:
    q = free_text.lower()
    metrics = [
        m for m in metrics
        if q in m["display_name"].lower()
        or q in (m.get("description") or "").lower()
        or q in (m.get("calculation_description") or "").lower()
        or q in m["metric_id"].lower()
    ]

# ---------------------------------------------------------------------------
# Catalog table
# ---------------------------------------------------------------------------
if not metrics:
    st.info("No metrics match the current filters.")
    st.stop()

table_rows = []
for m in metrics:
    table_rows.append({
        "ID": m["metric_id"],
        "Metric": m["display_name"],
        "Domain": DOMAIN_MAP.get(m["domain_id"], m["domain_id"]),
        "Tier": m["tier"],
        "Type": m["metric_type"],
        "Status": m["status"].replace("_", " ").title(),
        "Owner": m["owner_name"],
        "dbt ✓": "✅" if m.get("has_dbt_model") else "—",
        "Semantic View": "✅" if m.get("semantic_view_ref") else "—",
    })

df = pd.DataFrame(table_rows)

st.caption(f"Showing {len(metrics)} metric(s)")

event = st.dataframe(
    df,
    width="stretch",
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row",
    column_config={
        "Tier": st.column_config.TextColumn("Tier", width="small"),
        "dbt ✓": st.column_config.TextColumn("dbt", width="small"),
        "Semantic View": st.column_config.TextColumn("Sem. View", width="small"),
    },
)

# ---------------------------------------------------------------------------
# Detail panel — appears when a row is selected
# ---------------------------------------------------------------------------
selected_rows = event.selection.rows if event.selection else []

# Also support navigation from other pages via session state
if st.session_state.get("selected_metric_id"):
    nav_id = st.session_state.selected_metric_id
    nav_metric = next((m for m in st.session_state.metrics if m["metric_id"] == nav_id), None)
    if nav_metric:
        selected_metric = nav_metric
        st.session_state.selected_metric_id = None  # consume
        selected_rows = []  # skip table selection
    else:
        selected_metric = None
elif selected_rows:
    idx = selected_rows[0]
    selected_id = metrics[idx]["metric_id"]
    selected_metric = next((m for m in st.session_state.metrics if m["metric_id"] == selected_id), None)
else:
    selected_metric = None

# ---------------------------------------------------------------------------
# Detail panel render
# ---------------------------------------------------------------------------
# Re-check selection
if selected_rows:
    idx = selected_rows[0]
    if idx < len(metrics):
        selected_id = metrics[idx]["metric_id"]
        m = next((x for x in st.session_state.metrics if x["metric_id"] == selected_id), None)
        if m:
            st.divider()
            domain_name = DOMAIN_MAP.get(m["domain_id"], m["domain_id"])
            tier = m["tier"]
            status = m["status"]

            tier_badge = {"T1": "🔴 T1 — Critical / Regulatory", "T2": "🟠 T2 — Operational", "T3": "⚫ T3 — Exploratory"}.get(tier, tier)
            status_badge = {"approved": "✅ Approved", "under_review": "🔵 Under Review", "draft": "⚪ Draft", "deprecated": "❌ Deprecated"}.get(status, status)

            header_col, badges_col = st.columns([3, 2])
            with header_col:
                st.subheader(m["display_name"])
                st.caption(f"`{m['metric_id']}` · {domain_name} · {m['metric_type'].title()} · {m['granularity'].title()}")
            with badges_col:
                st.markdown(f"{tier_badge} &nbsp;&nbsp; {status_badge}", unsafe_allow_html=True)
                st.caption(f"Owner: **{m['owner_name']}** · {m['owner_role']}")

            tab_overview, tab_dims, tab_deps, tab_tech, tab_dict = st.tabs(
                ["Overview", "Dimensions", "Dependencies", "Technical", "Dictionary Links"]
            )

            with tab_overview:
                st.markdown("**Description**")
                st.write(m.get("description") or "—")
                st.markdown("**Business Calculation**")
                st.write(m.get("calculation_description") or "—")
                if m.get("formula_sql"):
                    st.markdown("**Formula SQL**")
                    st.code(m["formula_sql"], language="sql")
                else:
                    st.caption("No SQL formula registered.")
                tags = [t["tag"] for t in METRIC_TAGS if t["metric_id"] == m["metric_id"]]
                if tags:
                    st.markdown("**Tags:** " + "  ".join([f"`{t}`" for t in tags]))

            with tab_dims:
                linked = [md for md in METRIC_DIMENSIONS if md["metric_id"] == m["metric_id"]]
                if linked:
                    dim_rows = []
                    for md in linked:
                        dim = next((d for d in DIMENSIONS if d["dimension_id"] == md["dimension_id"]), None)
                        if dim:
                            dim_rows.append({
                                "Dimension": dim["display_name"],
                                "Name": dim["dimension_name"],
                                "Scope": DOMAIN_MAP.get(dim.get("domain_id"), "Cross-domain") if dim.get("domain_id") else "Cross-domain",
                                "Default": "✅" if md["is_default"] else "—",
                                "Values": (dim.get("possible_values") or "")[:60],
                            })
                    st.dataframe(pd.DataFrame(dim_rows), width="stretch", hide_index=True)
                else:
                    st.caption("No dimensions registered for this metric.")

            with tab_deps:
                parents = [d for d in METRIC_DEPENDENCIES if d["child_metric_id"] == m["metric_id"]]
                children = [d for d in METRIC_DEPENDENCIES if d["parent_metric_id"] == m["metric_id"]]
                if parents:
                    st.markdown("**Used by (parent metrics)**")
                    for dep in parents:
                        pm = next((x for x in st.session_state.metrics if x["metric_id"] == dep["parent_metric_id"]), None)
                        if pm:
                            st.markdown(f"- `{pm['metric_id']}` {pm['display_name']} — *{dep['relationship_type']}*")
                if children:
                    st.markdown("**Depends on (input metrics)**")
                    for dep in children:
                        cm = next((x for x in st.session_state.metrics if x["metric_id"] == dep["child_metric_id"]), None)
                        if cm:
                            st.markdown(f"- `{cm['metric_id']}` {cm['display_name']} — *{dep['relationship_type']}*")
                if not parents and not children:
                    st.caption("No dependencies registered.")

            with tab_tech:
                sync = METRIC_TECHNICAL_SYNC.get(m["metric_id"])
                if sync:
                    col_t1, col_t2 = st.columns(2)
                    with col_t1:
                        st.markdown("**dbt Model**")
                        st.code(sync["dbt_model_path"], language="text")
                        status_icon = "✅" if sync["dbt_run_status"] == "success" else "❌"
                        tests_icon = "✅" if sync["dbt_tests_passing"] else "❌"
                        st.markdown(f"Run status: {status_icon} `{sync['dbt_run_status']}`")
                        st.markdown(f"Tests passing: {tests_icon}")
                        st.caption(f"Last dbt run: `{sync['last_dbt_run']}`")
                    with col_t2:
                        st.markdown("**Snowflake**")
                        st.markdown(f"Source table: `{sync['source_table']}`")
                        if sync.get("semantic_view_ref"):
                            st.markdown(f"Semantic view: `{sync['semantic_view_ref']}`")
                            if sync.get("yaml_path"):
                                st.code(sync["yaml_path"], language="text")
                        else:
                            st.caption("No Snowflake Semantic View yet.")
                        st.caption(f"Last synced: `{sync['last_synced_at']}`")
                else:
                    if m.get("semantic_view_ref"):
                        st.markdown(f"**Semantic view:** `{m['semantic_view_ref']}`")
                    elif m.get("has_dbt_model"):
                        st.markdown("**Implementation stage:** dbt Model")
                    else:
                        st.markdown("**Implementation stage:** Registry Only")
                    st.caption("No CI/CD sync record found for this metric.")

            with tab_dict:
                links = [l for l in METRIC_DICTIONARY_LINKS if l["metric_id"] == m["metric_id"]]
                if links:
                    link_rows = [{"Term": l["dictionary_term"], "Relationship": l["relationship"]} for l in links]
                    st.dataframe(pd.DataFrame(link_rows), width="stretch", hide_index=True)
                else:
                    st.caption("No dictionary links registered for this metric.")

elif st.session_state.get("selected_metric_id"):
    nav_id = st.session_state.selected_metric_id
    m = next((x for x in st.session_state.metrics if x["metric_id"] == nav_id), None)
    st.session_state.selected_metric_id = None
    if m:
        st.info(f"Navigated to metric **{m['display_name']}** (`{m['metric_id']}`). Use the filters above to find and select it.")
