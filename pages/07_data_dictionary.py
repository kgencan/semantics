"""
F6 — Data Dictionary
Insurance terminology linked to governed metrics.
"""

import streamlit as st
import pandas as pd
from data.seed_data import DICTIONARY_TERMS, METRIC_DICTIONARY_LINKS, DOMAINS


# ---------------------------------------------------------------------------
# Session state init
# ---------------------------------------------------------------------------
if "metrics" not in st.session_state:
    from data.seed_data import METRICS
    st.session_state.metrics = [dict(m) for m in METRICS]
if "selected_dict_term" not in st.session_state:
    st.session_state.selected_dict_term = None

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
DOMAIN_MAP = {d["domain_id"]: d["domain_name"] for d in DOMAINS}

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.markdown("# :material/book: Data Dictionary")
st.caption(
    f"{len(DICTIONARY_TERMS)} governed terms · Linked to metrics in the Semantics registry.  \n"
    "These terms ensure metric calculations reference standardized business definitions."
)

st.divider()

# ---------------------------------------------------------------------------
# Two-column layout
# ---------------------------------------------------------------------------
left_col, right_col = st.columns([1, 2], gap="large")

with left_col:
    st.markdown("**Terms**")

    search = st.text_input("Search terms…", placeholder="e.g. Premium, IBNR, LICAT", label_visibility="collapsed")

    filtered_terms = DICTIONARY_TERMS
    if search:
        q = search.lower()
        filtered_terms = [
            t for t in DICTIONARY_TERMS
            if q in t["term"].lower() or q in t["definition"].lower() or q in (t.get("regulatory_ref") or "").lower()
        ]

    st.caption(f"{len(filtered_terms)} term(s)")

    for term in filtered_terms:
        # Count linked metrics
        linked_count = sum(1 for l in METRIC_DICTIONARY_LINKS if l["dictionary_term"] == term["term"])
        label = f"**{term['term']}**"
        if linked_count > 0:
            label += f" · {linked_count} metric(s)"

        is_selected = st.session_state.selected_dict_term == term["term"]
        if st.button(
            term["term"] + (f" ({linked_count})" if linked_count else ""),
            key=f"term_btn_{term['term']}",
            width="stretch",
            type="primary" if is_selected else "secondary",
        ):
            st.session_state.selected_dict_term = term["term"]
            st.rerun()

with right_col:
    selected_term_name = st.session_state.selected_dict_term

    if not selected_term_name:
        st.info("Select a term from the left panel to see its definition and linked metrics.")
        st.markdown("**Why does the dictionary matter?**")
        st.markdown(
            "When metrics reference the same term (e.g. *Net Earned Premium*) but use different definitions, "
            "they produce different numbers. The Data Dictionary anchors every metric to a shared, standardized definition — "
            "the same one used in regulatory filings, actuarial reports, and board packages."
        )
    else:
        term = next((t for t in DICTIONARY_TERMS if t["term"] == selected_term_name), None)

        if term:
            st.subheader(term["term"])
            if term.get("regulatory_ref"):
                st.caption(f"📄 Regulatory reference: **{term['regulatory_ref']}**")

            st.markdown("**Definition**")
            st.write(term["definition"])

            st.divider()

            # Linked metrics
            links = [l for l in METRIC_DICTIONARY_LINKS if l["dictionary_term"] == term["term"]]
            if links:
                st.markdown(f"**Metrics using this term** ({len(links)})")
                rows = []
                for l in links:
                    m = next((x for x in st.session_state.metrics if x["metric_id"] == l["metric_id"]), None)
                    if m:
                        tier_icon = {"T1": "🔴", "T2": "🟠", "T3": "⚫"}.get(m["tier"], "")
                        status_icon = {"approved": "✅", "under_review": "🔵", "draft": "⚪", "deprecated": "❌"}.get(m["status"], "")
                        rows.append({
                            "ID": m["metric_id"],
                            "Metric": m["display_name"],
                            "Relationship": l["relationship"],
                            "Domain": DOMAIN_MAP.get(m["domain_id"], m["domain_id"]),
                            "Tier": f"{tier_icon} {m['tier']}",
                            "Status": f"{status_icon} {m['status'].replace('_', ' ').title()}",
                        })
                st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

                # Link to catalog
                for l in links:
                    if st.button(f"📋 View {l['metric_id']} in Catalog →", key=f"view_{l['metric_id']}_{term['term']}"):
                        st.session_state.selected_metric_id = l["metric_id"]
                        st.switch_page("pages/01_catalog.py")
            else:
                st.caption("No metrics currently linked to this term.")

            # Conflict note: highlight if term appears in reconciliation findings
            if "reconciliation_log" in st.session_state:
                term_conflicts = []
                for f in st.session_state.reconciliation_log:
                    if f["status"] == "open" and term["term"].lower() in (f.get("description") or "").lower():
                        term_conflicts.append(f)
                if term_conflicts:
                    st.divider()
                    st.warning(
                        f"⚠️ **{len(term_conflicts)} open reconciliation finding(s)** reference this term.  \n"
                        "Conflicting definitions of **" + term["term"] + "** may be contributing to cross-domain contradictions."
                    )
                    for f in term_conflicts[:2]:
                        sev_icon = {"critical": "🔴", "warning": "🟠", "info": "🔵"}.get(f["severity"], "")
                        st.caption(f"{sev_icon} {f['finding_id']} · {f['domain_a']}" + (f" ↔ {f['domain_b']}" if f.get("domain_b") else ""))
                    if st.button("View in Reconciliation Dashboard →"):
                        st.switch_page("pages/05_reconciliation.py")
