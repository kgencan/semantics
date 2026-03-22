"""
F4 — AI Reconciliation Dashboard
Centerpiece of the demo — cross-domain conflict detection, severity-ordered findings,
interactive acknowledge/dismiss, and pre-fill to Change Requests.
"""

import streamlit as st
import pandas as pd
from data.seed_data import DOMAINS, METRICS as SEED_METRICS
from utils.kpi import kpi


# ---------------------------------------------------------------------------
# Session state init
# ---------------------------------------------------------------------------
if "reconciliation_log" not in st.session_state:
    from data.seed_data import RECONCILIATION_LOG
    st.session_state.reconciliation_log = [dict(f) for f in RECONCILIATION_LOG]
if "metrics" not in st.session_state:
    st.session_state.metrics = [dict(m) for m in SEED_METRICS]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
DOMAIN_NAMES = [d["domain_name"] for d in DOMAINS]
DOMAIN_MAP = {d["domain_id"]: d["domain_name"] for d in DOMAINS}

def metric_display(metric_id, metrics):
    if not metric_id:
        return None
    m = next((x for x in metrics if x["metric_id"] == metric_id), None)
    if m:
        return f"`{m['metric_id']}` {m['display_name']}"
    return f"`{metric_id}`"

SEVERITY_ICON = {"critical": "🔴", "warning": "🟠", "info": "🔵"}
TYPE_ICON = {
    "contradiction": "⚡ Contradiction",
    "duplicate": "🔁 Duplicate",
    "overlap": "🔀 Overlap",
    "gap": "⬜ Gap",
    "suggestion": "💡 Suggestion",
}
STATUS_ICON = {
    "open": "🔓 Open",
    "acknowledged": "👁 Acknowledged",
    "resolved": "✅ Resolved",
    "dismissed": "🚫 Dismissed",
}

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.markdown("# :material/sync: Reconciliation Dashboard")
st.caption("Last reconciliation run: **2026-03-12** · 40 metrics analyzed · 18 findings generated · Semantics Reconciliation Engine v0.2")

# Banner if new metrics were registered since last run
seed_ids = {m["metric_id"] for m in SEED_METRICS}
new_metrics = [m for m in st.session_state.metrics if m["metric_id"] not in seed_ids]
if new_metrics:
    names = ", ".join(m["display_name"] for m in new_metrics[:3])
    extra = f" (+{len(new_metrics)-3} more)" if len(new_metrics) > 3 else ""
    st.info(
        f"ℹ️ **{len(new_metrics)} new metric(s) registered since last run:** {names}{extra}  \n"
        "A full re-run would analyze them for cross-domain conflicts."
    )

col_btn, _ = st.columns([2, 8])
with col_btn:
    st.button(
        "🔄 Re-run Analysis",
        disabled=True,
        help="Requires Snowflake Cortex connection. In production, triggers the reconciliation engine against the full metric registry.",
        width="stretch",
    )

st.divider()

# ---------------------------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------------------------
log = st.session_state.reconciliation_log

total = len(log)
critical = sum(1 for f in log if f["severity"] == "critical")
warning = sum(1 for f in log if f["severity"] == "warning")
info = sum(1 for f in log if f["severity"] == "info")
open_count = sum(1 for f in log if f["status"] == "open")
resolved_count = sum(1 for f in log if f["status"] in ("resolved", "dismissed"))
acknowledged_count = sum(1 for f in log if f["status"] == "acknowledged")

critical_open = sum(1 for f in log if f["severity"] == "critical" and f["status"] == "open")
warning_open  = sum(1 for f in log if f["severity"] == "warning"  and f["status"] == "open")
info_open     = sum(1 for f in log if f["severity"] == "info"     and f["status"] == "open")

c1, c2, c3, c4, c5, c6 = st.columns(6)
kpi(c1, "Total Findings",        total)
kpi(c2, "Critical",              critical_open, accent_color="#B91C1C")
kpi(c3, "Warning",               warning_open,  accent_color="#D97706")
kpi(c4, "Info",                  info_open,  accent_color="#2563EB")
kpi(c5, "Open",                  open_count)
kpi(c6, "Resolved / Dismissed",  resolved_count + acknowledged_count)

st.divider()

# ---------------------------------------------------------------------------
# Cross-Domain Conflict Map  (the hero visual)
# ---------------------------------------------------------------------------
st.subheader("Cross-Domain Conflict Map")
st.caption("Colored by worst severity of open findings between each domain pair.")

short_names = {
    "Customer & Party": "Customer",
    "Policy & Coverage": "Policy",
    "Distribution & Sales": "Distribution",
    "Underwriting & New Business": "Underwriting",
    "Claims": "Claims",
    "Operations & Service": "Operations",
    "Finance & Actuarial": "Finance",
    "Investment": "Investment",
}
snames = list(short_names.values())

# Build per-severity count + worst-severity matrices
sev_rank = {"critical": 3, "warning": 2, "info": 1}
sev_counts = {(a, b): {"critical": 0, "warning": 0, "info": 0} for a in snames for b in snames}
sev_matrix = {(a, b): None for a in snames for b in snames}

for f in log:
    if f["status"] not in ("open", "acknowledged"):
        continue
    da = short_names.get(f["domain_a"], f["domain_a"])
    db = short_names.get(f.get("domain_b", ""), "")
    if da and db and da != db:
        sv = f["severity"]
        for pair in [(da, db), (db, da)]:
            sev_counts[pair][sv] += 1
            if sev_matrix[pair] is None or sev_rank[sv] > sev_rank.get(sev_matrix[pair], 0):
                sev_matrix[pair] = sv

def cell_label(pair):
    c = sev_counts[pair]
    parts = []
    if c["critical"]: parts.append(f"{c['critical']} CRIT.")
    if c["warning"]:  parts.append(f"{c['warning']} WARN.")
    if c["info"]:     parts.append(f"{c['info']} INFO")
    return " | ".join(parts)

# Severity → (background, text color)
SEV_STYLE = {
    "critical": ("#FEE2E2", "#B91C1C"),
    "warning":  ("#FEF3C7", "#92400E"),
    "info":     ("#EFF6FF", "#1D4ED8"),
}

# Shared cell style (no text-transform — consistent with row labels)
_TH_BASE = "padding:7px 12px;font-size:11px;font-weight:700;color:#3d4452;background:#eceef2;border:1px solid #d1d5de;white-space:nowrap;"
TH       = f'style="{_TH_BASE}text-align:left;"'
TH_COL   = f'style="{_TH_BASE}text-align:center;"'
TD_LABEL = f'style="{_TH_BASE}"'
TD_SELF  = 'style="background:#f5f6f8;border:1px solid #e4e6ed;"'
TD_EMPTY = 'style="background:#ffffff;border:1px solid #e4e6ed;text-align:center;color:#d1d5de;font-size:11px;"'

header_cells = "".join(f"<th {TH_COL}>{n}</th>" for n in snames)
header_row = f"<tr><th {TH}></th>{header_cells}</tr>"

body_rows = []
for row in snames:
    cells = [f"<td {TD_LABEL}>{row}</td>"]
    for col in snames:
        if row == col:
            cells.append(f"<td {TD_SELF}></td>")
        else:
            sev = sev_matrix[(row, col)]
            if sev is None:
                cells.append(f"<td {TD_EMPTY}>—</td>")
            else:
                bg, _ = SEV_STYLE[sev]
                label  = cell_label((row, col))
                cells.append(
                    f'<td style="background:{bg};color:#111318;border:1px solid #d1d5de;'
                    f'text-align:center;padding:7px 12px;font-size:11px;font-weight:600;white-space:nowrap;">'
                    f"{label}</td>"
                )
    body_rows.append(f"<tr>{''.join(cells)}</tr>")

st.markdown(f"""
<div style="overflow-x:auto;">
<table style="border-collapse:collapse;width:100%;">
  <thead>{header_row}</thead>
  <tbody>{''.join(body_rows)}</tbody>
</table>
</div>
""", unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------
fc1, fc2, fc3, fc4 = st.columns(4)

with fc1:
    filter_type = st.multiselect(
        "Finding Type",
        ["contradiction", "duplicate", "overlap", "gap", "suggestion"],
        placeholder="All types",
        format_func=lambda t: TYPE_ICON.get(t, t),
    )
with fc2:
    filter_severity = st.multiselect(
        "Severity",
        ["critical", "warning", "info"],
        placeholder="All severities",
        format_func=lambda s: f"{SEVERITY_ICON.get(s, '')} {s.title()}",
    )
with fc3:
    filter_domain = st.selectbox(
        "Domain",
        ["All domains"] + DOMAIN_NAMES,
        placeholder="All domains",
    )
with fc4:
    filter_status = st.selectbox(
        "Status",
        ["All", "open", "acknowledged", "resolved", "dismissed"],
        format_func=lambda s: STATUS_ICON.get(s, s.title()) if s != "All" else "All statuses",
    )

# Apply filters
filtered = log[:]

if filter_type:
    filtered = [f for f in filtered if f["finding_type"] in filter_type]
if filter_severity:
    filtered = [f for f in filtered if f["severity"] in filter_severity]
if filter_domain and filter_domain != "All domains":
    filtered = [f for f in filtered if f["domain_a"] == filter_domain or f.get("domain_b") == filter_domain]
if filter_status and filter_status != "All":
    filtered = [f for f in filtered if f["status"] == filter_status]

st.caption(f"Showing {len(filtered)} of {total} findings")

if not filtered:
    st.info("No findings match the current filters.")
    st.stop()

# ---------------------------------------------------------------------------
# Finding cards — grouped by severity
# ---------------------------------------------------------------------------
def render_finding_card(f):
    severity = f["severity"]
    finding_type = f["finding_type"]
    status = f["status"]

    sev_icon = SEVERITY_ICON.get(severity, "")
    type_label = TYPE_ICON.get(finding_type, finding_type.title())
    status_label = STATUS_ICON.get(status, status)

    domain_b_label = f.get("domain_b") or ""
    domains_label = f["domain_a"] + (f" ↔ {domain_b_label}" if domain_b_label else "")

    metric_a = metric_display(f.get("metric_a_id"), st.session_state.metrics)
    metric_b = metric_display(f.get("metric_b_id"), st.session_state.metrics)

    with st.container(border=True):
        header_l, header_r = st.columns([4, 2])
        with header_l:
            st.markdown(
                f"{sev_icon} **{type_label}** &nbsp;&nbsp; `{f['finding_id']}`",
                unsafe_allow_html=True,
            )
            st.caption(f"**{domains_label}**")
            if metric_a or metric_b:
                metric_line = "  →  ".join(filter(None, [metric_a, metric_b]))
                st.caption(metric_line)
        with header_r:
            st.markdown(f"**{status_label}**")
            st.caption(f"Run: {f['run_date']}")

        st.markdown(f.get("description", ""))

        if f.get("suggested_resolution"):
            st.info(f"💡 **Suggested resolution:** {f['suggested_resolution']}")

        if status == "open" or status == "acknowledged":
            btn1, btn2, btn3, _ = st.columns([1, 1, 2, 2])

            with btn1:
                if status == "open":
                    if st.button("👁 Acknowledge", key=f"ack_{f['finding_id']}", width="stretch"):
                        for item in st.session_state.reconciliation_log:
                            if item["finding_id"] == f["finding_id"]:
                                item["status"] = "acknowledged"
                                item["resolved_by"] = "Demo User"
                                break
                        st.rerun()

            with btn2:
                if st.button("🚫 Dismiss", key=f"dis_{f['finding_id']}", width="stretch"):
                    for item in st.session_state.reconciliation_log:
                        if item["finding_id"] == f["finding_id"]:
                            item["status"] = "dismissed"
                            break
                    st.rerun()

            with btn3:
                if st.button("📝 Create Change Request →", key=f"cr_{f['finding_id']}", width="stretch"):
                    domain_id = next(
                        (d["domain_id"] for d in DOMAINS if d["domain_name"] == f["domain_a"]), None
                    )
                    st.session_state.cr_prefill_domain = domain_id
                    st.session_state.cr_prefill_title = f"Resolve {f['finding_id']}: {TYPE_ICON.get(f['finding_type'], '')} in {f['domain_a']}"
                    st.session_state.cr_prefill_description = (
                        f"Reconciliation finding {f['finding_id']} ({f['finding_type']} · {f['severity']}):\n\n"
                        + f.get("description", "")
                        + "\n\nSuggested resolution:\n"
                        + f.get("suggested_resolution", "")
                    )
                    st.switch_page("pages/04_change_requests.py")

            if metric_a and f.get("metric_a_id"):
                with _:
                    if st.button(f"📋 View {f['metric_a_id']} →", key=f"view_{f['finding_id']}", width="stretch"):
                        st.session_state.selected_metric_id = f["metric_a_id"]
                        st.switch_page("pages/01_catalog.py")


# Critical section
critical_findings = [f for f in filtered if f["severity"] == "critical"]
if critical_findings:
    st.subheader(f"🔴 Critical — Immediate Action Required ({len(critical_findings)})")
    for f in critical_findings:
        render_finding_card(f)
    st.divider()

# Warning section
warning_findings = [f for f in filtered if f["severity"] == "warning"]
if warning_findings:
    st.subheader(f"🟠 Warnings — Review Recommended ({len(warning_findings)})")
    for f in warning_findings:
        render_finding_card(f)
    st.divider()

# Info section
info_findings = [f for f in filtered if f["severity"] == "info"]
if info_findings:
    st.subheader(f"🔵 Informational ({len(info_findings)})")
    for f in info_findings:
        render_finding_card(f)
