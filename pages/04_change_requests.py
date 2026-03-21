"""
F3b — Change Request Workflow
Modify, deprecate, or question existing metrics. Pre-fillable from Reconciliation page.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from data.seed_data import DOMAINS
from utils.fuzzy import detect_duplicates
from utils.nav import render_sidebar

st.set_page_config(page_title="Change Requests · Semantics", page_icon="◈", layout="wide")

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
if "change_requests" not in st.session_state:
    st.session_state.change_requests = []

# ---------------------------------------------------------------------------
# Pre-fill from Reconciliation page
# ---------------------------------------------------------------------------
DOMAIN_MAP = {d["domain_id"]: d["domain_name"] for d in DOMAINS}
DOMAIN_BY_NAME = {d["domain_name"]: d for d in DOMAINS}
DOMAIN_BY_ID = {d["domain_id"]: d for d in DOMAINS}

prefill_domain_id = st.session_state.pop("cr_prefill_domain", None)
prefill_title = st.session_state.pop("cr_prefill_title", None)
prefill_description = st.session_state.pop("cr_prefill_description", None)

# Persist pre-fills in form-specific session state so they survive rerun
if prefill_domain_id and "cr_form_domain" not in st.session_state:
    st.session_state.cr_form_domain = prefill_domain_id
if prefill_title and "cr_form_title" not in st.session_state:
    st.session_state.cr_form_title = prefill_title
if prefill_description and "cr_form_description" not in st.session_state:
    st.session_state.cr_form_description = prefill_description

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("📝 Change Requests")

if st.session_state.get("cr_form_domain") or st.session_state.get("cr_form_title"):
    st.success("📋 Form pre-filled from a Reconciliation finding. Review and submit.")

st.caption(
    "Use this form to propose modifications, deprecations, or to ask questions about existing metrics.  \n"
    "To register a *new* metric, use **Register Metric** instead."
)

# ---------------------------------------------------------------------------
# Layout: form left, submitted requests right
# ---------------------------------------------------------------------------
form_col, table_col = st.columns([3, 2], gap="large")

with form_col:
    domain_names = [d["domain_name"] for d in DOMAINS]

    # Determine default domain index
    default_domain_name = None
    if st.session_state.get("cr_form_domain"):
        default_domain_name = DOMAIN_MAP.get(st.session_state.cr_form_domain)
    default_domain_idx = domain_names.index(default_domain_name) if default_domain_name in domain_names else 0

    with st.form("change_request_form", clear_on_submit=True):
        st.markdown("### Change Request")

        request_type = st.radio(
            "Request Type *",
            ["modify", "deprecate", "question"],
            horizontal=True,
            format_func=lambda t: {"modify": "✏️ Modify", "deprecate": "🗑 Deprecate", "question": "❓ Question"}.get(t, t),
        )

        st.divider()

        # Domain + metric selection
        col_d, col_m = st.columns(2)
        with col_d:
            domain_selected_name = st.selectbox(
                "Domain *",
                domain_names,
                index=default_domain_idx,
            )
        with col_m:
            domain_id_sel = next((d["domain_id"] for d in DOMAINS if d["domain_name"] == domain_selected_name), None)
            domain_metrics = [m for m in st.session_state.metrics if m["domain_id"] == domain_id_sel]
            metric_options = {m["display_name"]: m["metric_id"] for m in domain_metrics}
            metric_name_sel = st.selectbox(
                "Metric",
                ["— Select a metric —"] + list(metric_options.keys()),
            )
        metric_id_sel = metric_options.get(metric_name_sel) if metric_name_sel != "— Select a metric —" else None

        st.divider()

        # Requester
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            requester = st.text_input("Your Name *", placeholder="e.g. Marc Leclair")
        with col_r2:
            requester_role = st.text_input("Your Role *", placeholder="e.g. Senior Data Analyst")

        st.divider()

        # Request content
        title = st.text_input(
            "Title *",
            value=st.session_state.get("cr_form_title", ""),
            placeholder="Brief summary of the request",
        )

        description = st.text_area(
            "Description *",
            value=st.session_state.get("cr_form_description", ""),
            placeholder="What change are you requesting, or what question are you raising?",
            height=120,
        )

        business_justification = st.text_area(
            "Business Justification *",
            placeholder="Why is this change needed? What is the business impact?",
            height=80,
        )

        proposed_definition = None
        if request_type == "modify":
            proposed_definition = st.text_area(
                "Proposed New Definition",
                placeholder="If modifying the calculation or description, provide the proposed new text.",
                height=80,
            )

        submitted = st.form_submit_button("Submit Request →", type="primary", use_container_width=True)

    if submitted:
        errors = []
        if not requester.strip():
            errors.append("Your name is required.")
        if not requester_role.strip():
            errors.append("Your role is required.")
        if not title.strip():
            errors.append("Title is required.")
        if not description.strip():
            errors.append("Description is required.")
        if not business_justification.strip():
            errors.append("Business justification is required.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            now = datetime.now().isoformat(timespec="seconds")
            seq = len(st.session_state.change_requests) + 1
            new_cr = {
                "request_id": f"CR-{seq:03d}",
                "metric_id": metric_id_sel,
                "request_type": request_type,
                "requester": requester.strip(),
                "requester_role": requester_role.strip(),
                "domain_id": domain_id_sel,
                "title": title.strip(),
                "description": description.strip(),
                "business_justification": business_justification.strip(),
                "proposed_definition": proposed_definition.strip() if proposed_definition else None,
                "status": "submitted",
                "reviewer": None,
                "review_notes": None,
                "created_at": now,
                "resolved_at": None,
            }
            st.session_state.change_requests.append(new_cr)

            # Clear pre-fill state
            for key in ("cr_form_domain", "cr_form_title", "cr_form_description"):
                st.session_state.pop(key, None)

            st.success(f"✅ Change request **{new_cr['request_id']}** submitted and routed to **{domain_selected_name}** champion.")
            st.rerun()

with table_col:
    st.markdown("### Submitted Requests")

    crs = st.session_state.change_requests
    if not crs:
        st.info("No change requests submitted yet in this session.")
        st.caption("Submit a request using the form, or navigate from a Reconciliation finding to pre-fill.")
    else:
        rows = []
        for cr in reversed(crs):
            domain_label = DOMAIN_MAP.get(cr.get("domain_id"), "—")
            type_label = {"modify": "✏️ Modify", "deprecate": "🗑 Deprecate", "question": "❓ Question", "new": "➕ New"}.get(cr["request_type"], cr["request_type"].title())
            rows.append({
                "ID": cr["request_id"],
                "Type": type_label,
                "Title": cr["title"][:50] + ("…" if len(cr["title"]) > 50 else ""),
                "Domain": domain_label,
                "Requester": cr["requester"],
                "Status": cr["status"].title(),
                "Submitted": cr["created_at"][:10],
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # Workflow info
        st.divider()
        st.markdown("**Workflow**")
        st.markdown("""
```
submitted
    ↓
in_review  (domain champion reviews)
    ↓
approved / rejected
    ↓
implemented
```
""")
        st.caption(
            "T1 requests require cross-domain review.  \n"
            "T2 requires domain champion approval.  \n"
            "T3 is self-service."
        )
