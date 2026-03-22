"""
F3a — Register New Metric
Primary demo entry point for non-technical audiences.
Guided metric registration with live preview and fuzzy duplicate detection.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from data.seed_data import DOMAINS
from utils.fuzzy import detect_duplicates


# ---------------------------------------------------------------------------
# Session state init
# ---------------------------------------------------------------------------
if "metrics" not in st.session_state:
    from data.seed_data import METRICS
    st.session_state.metrics = [dict(m) for m in METRICS]

if "new_metric_submitted" not in st.session_state:
    st.session_state.new_metric_submitted = None

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
DOMAIN_MAP = {d["domain_id"]: d["domain_name"] for d in DOMAINS}
DOMAIN_BY_NAME = {d["domain_name"]: d for d in DOMAINS}
TIER_INFO = {
    "T1": "Critical / Regulatory — board-reported KPIs, OSFI metrics, IFRS 17 disclosures. Requires domain champion + cross-domain review.",
    "T2": "Operational — standard domain KPIs used in regular reporting. Requires domain champion approval.",
    "T3": "Exploratory — ad hoc analysis, experimental metrics, team-level tracking. Self-registered, no formal approval.",
}

def next_metric_id(domain_id: str, metrics: list) -> str:
    prefix = domain_id.split("-")[0][:3].upper()
    # Map domain prefix
    prefix_map = {
        "DOM-01": "CUS", "DOM-02": "POL", "DOM-03": "DIS",
        "DOM-04": "UND", "DOM-05": "CLM", "DOM-06": "OPS",
        "DOM-07": "FIN", "DOM-08": "INV",
    }
    pfx = prefix_map.get(domain_id, "MET")
    existing = [m["metric_id"] for m in metrics if m["metric_id"].startswith(pfx)]
    max_num = 0
    for mid in existing:
        try:
            num = int(mid.split("-")[1])
            if num > max_num:
                max_num = num
        except (IndexError, ValueError):
            pass
    return f"{pfx}-{max_num + 1:03d}"

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.markdown("# :material/add: Register a New Metric")

# Framing card
with st.container(border=True):
    st.markdown(
        "**What does registering a metric mean?**  \n"
        "It means giving a business concept an official definition, an owner, and a governance tier — *before* any code is written.  \n"
        "This is the first step from ad-hoc data to governed analytics that AI agents and reports can trust."
    )

st.divider()

# ---------------------------------------------------------------------------
# Check if already submitted (show success state)
# ---------------------------------------------------------------------------
if st.session_state.new_metric_submitted:
    submitted = st.session_state.new_metric_submitted
    domain = DOMAIN_MAP.get(submitted.get("domain_id"), "")
    champion = next((d["champion_name"] for d in DOMAINS if d["domain_id"] == submitted.get("domain_id")), "the domain champion")

    st.success(f"✅ Metric **{submitted['display_name']}** registered as `{submitted['metric_id']}` with status **Draft**.")

    with st.container(border=True):
        st.markdown("**What happens next?**")
        st.markdown(
            f"Your metric is now in `draft` status in the **{domain}** domain.  \n"
            f"**{champion}** will review the definition and calculation logic.  \n\n"
            "Once approved:  \n"
            "- A **dbt model** will be created in `marts/{domain}/` to source the data  \n"
            "- A **Snowflake Semantic View** will be materialised in `ANALYTICS.SEMANTIC_VIEWS`  \n"
            "- The metric becomes queryable by **Cortex Analyst** for natural language reporting"
        )

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("📋 View in Metric Catalog", width="stretch"):
            st.session_state.selected_metric_id = submitted["metric_id"]
            st.session_state.new_metric_submitted = None
            st.switch_page("pages/01_catalog.py")
    with col_b:
        if st.button("📝 Submit a Change Request to promote to T2", width="stretch"):
            st.session_state.cr_prefill_domain = submitted.get("domain_id")
            st.session_state.cr_prefill_title = f"Promote {submitted['display_name']} to T2"
            st.session_state.cr_prefill_description = f"Requesting promotion of {submitted['metric_id']} ({submitted['display_name']}) from T3 draft to T2 operational metric."
            st.session_state.new_metric_submitted = None
            st.switch_page("pages/04_change_requests.py")
    with col_c:
        if st.button("➕ Register another metric", width="stretch"):
            st.session_state.new_metric_submitted = None
            st.rerun()
    st.stop()

# ---------------------------------------------------------------------------
# Two-column layout: form (left) + live preview (right)
# ---------------------------------------------------------------------------
form_col, preview_col = st.columns([3, 2], gap="large")

# Form values tracked outside the form for live preview
if "nm_display_name" not in st.session_state:
    st.session_state.nm_display_name = ""
if "nm_domain_id" not in st.session_state:
    st.session_state.nm_domain_id = DOMAINS[0]["domain_id"]
if "nm_metric_type" not in st.session_state:
    st.session_state.nm_metric_type = "KPI"
if "nm_tier" not in st.session_state:
    st.session_state.nm_tier = "T3"
if "nm_description" not in st.session_state:
    st.session_state.nm_description = ""
if "nm_calculation" not in st.session_state:
    st.session_state.nm_calculation = ""
if "nm_formula_sql" not in st.session_state:
    st.session_state.nm_formula_sql = ""
if "nm_unit" not in st.session_state:
    st.session_state.nm_unit = "percentage"
if "nm_granularity" not in st.session_state:
    st.session_state.nm_granularity = "monthly"
if "nm_owner_name" not in st.session_state:
    st.session_state.nm_owner_name = ""
if "nm_owner_role" not in st.session_state:
    st.session_state.nm_owner_role = ""

with form_col:
    with st.form("register_metric_form", clear_on_submit=False):

        # ── Step 1: Identity ───────────────────────────────────────────────
        st.markdown("### Step 1 — Identity")

        display_name = st.text_input(
            "Metric Name *",
            value=st.session_state.nm_display_name,
            placeholder="e.g. First-Year Disability Lapse Rate",
            help="Human-readable name. Will appear in dashboards and reports.",
        )

        domain_names = [d["domain_name"] for d in DOMAINS]
        domain_idx = next(
            (i for i, d in enumerate(DOMAINS) if d["domain_id"] == st.session_state.nm_domain_id), 0
        )
        domain_name_selected = st.selectbox(
            "Domain *",
            domain_names,
            index=domain_idx,
            help="The domain that owns and governs this metric.",
        )
        selected_domain = DOMAIN_BY_NAME[domain_name_selected]

        # Show champion info
        st.caption(f"Domain champion: **{selected_domain['champion_name']}** · {selected_domain['champion_role']}")

        metric_type = st.selectbox(
            "Metric Type *",
            ["KPI", "operational", "financial", "actuarial", "regulatory", "derived"],
            index=["KPI", "operational", "financial", "actuarial", "regulatory", "derived"].index(
                st.session_state.nm_metric_type
            ),
        )

        tier = st.radio(
            "Governance Tier *",
            ["T1", "T2", "T3"],
            index=["T1", "T2", "T3"].index(st.session_state.nm_tier),
            horizontal=True,
            help="T1 = Critical/Regulatory · T2 = Operational · T3 = Exploratory",
        )
        tier_explanation = TIER_INFO.get(tier, "")
        st.caption(tier_explanation)

        st.divider()
        # ── Step 2: Definition ─────────────────────────────────────────────
        st.markdown("### Step 2 — Definition")

        description = st.text_area(
            "Description *",
            value=st.session_state.nm_description,
            placeholder="What does this metric measure? Write in plain business language.",
            height=80,
        )

        calculation = st.text_area(
            "Business Calculation *",
            value=st.session_state.nm_calculation,
            placeholder="How is it calculated? Describe in business terms, not SQL.",
            height=80,
        )

        formula_sql = st.text_area(
            "Formula SQL (optional)",
            value=st.session_state.nm_formula_sql,
            placeholder="e.g. policies_lapsed_year_1 / policies_issued_year_1",
            height=60,
        )

        col_unit, col_gran = st.columns(2)
        with col_unit:
            unit = st.selectbox(
                "Unit *",
                ["percentage", "CAD", "ratio", "count", "per_thousand", "factor"],
                index=["percentage", "CAD", "ratio", "count", "per_thousand", "factor"].index(
                    st.session_state.nm_unit
                ),
            )
        with col_gran:
            granularity = st.selectbox(
                "Granularity *",
                ["monthly", "quarterly", "annual", "daily"],
                index=["monthly", "quarterly", "annual", "daily"].index(
                    st.session_state.nm_granularity
                ),
            )

        st.divider()
        # ── Step 3: Ownership ──────────────────────────────────────────────
        st.markdown("### Step 3 — Ownership")

        col_own1, col_own2 = st.columns(2)
        with col_own1:
            owner_name = st.text_input(
                "Owner Name *",
                value=st.session_state.nm_owner_name or selected_domain["champion_name"],
                placeholder=selected_domain["champion_name"],
            )
        with col_own2:
            owner_role = st.text_input(
                "Owner Role *",
                value=st.session_state.nm_owner_role or selected_domain["champion_role"],
                placeholder=selected_domain["champion_role"],
            )

        st.divider()
        submitted = st.form_submit_button("Register Metric →", type="primary", width="stretch")

    # ── Fuzzy dedup (outside form, reactive) ──────────────────────────────
    if description or calculation:
        dupes = detect_duplicates(
            proposed_name=display_name,
            proposed_description=description,
            proposed_calculation=calculation,
            metrics=st.session_state.metrics,
            threshold=58,
        )
        if dupes:
            st.warning(
                f"⚠️ **Potential duplicate detected** — {len(dupes)} similar metric(s) already in the registry."
            )
            for d in dupes[:3]:
                domain_label = DOMAIN_MAP.get(d["domain_id"], d["domain_id"])
                tier_icon = {"T1": "🔴", "T2": "🟠", "T3": "⚫"}.get(d["tier"], "")
                status_icon = {"approved": "✅", "under_review": "🔵", "draft": "⚪"}.get(d["status"], "")
                with st.container(border=True):
                    st.markdown(
                        f"**{d['display_name']}** `{d['metric_id']}` · {tier_icon} {d['tier']} · {status_icon} {d['status'].replace('_',' ').title()}  \n"
                        f"Domain: *{domain_label}* · Similarity: **{d['similarity_score']}%**"
                    )
                    if st.button(f"View {d['metric_id']} in Catalog →", key=f"view_{d['metric_id']}"):
                        st.session_state.selected_metric_id = d["metric_id"]
                        st.switch_page("pages/01_catalog.py")

    # ── Handle submission ──────────────────────────────────────────────────
    if submitted:
        # Validation
        errors = []
        if not display_name.strip():
            errors.append("Metric name is required.")
        if not description.strip():
            errors.append("Description is required.")
        if not calculation.strip():
            errors.append("Business calculation is required.")
        if not owner_name.strip():
            errors.append("Owner name is required.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            domain_id = selected_domain["domain_id"]
            new_id = next_metric_id(domain_id, st.session_state.metrics)
            metric_name = display_name.strip().lower().replace(" ", "_").replace("-", "_")
            now = datetime.now().isoformat(timespec="seconds")

            new_metric = {
                "metric_id": new_id,
                "metric_name": metric_name,
                "display_name": display_name.strip(),
                "domain_id": domain_id,
                "description": description.strip(),
                "calculation_description": calculation.strip(),
                "formula_sql": formula_sql.strip() or None,
                "metric_type": metric_type,
                "tier": tier,
                "granularity": granularity,
                "unit": unit,
                "owner_name": owner_name.strip(),
                "owner_role": owner_role.strip(),
                "status": "draft",
                "has_dbt_model": False,
                "semantic_view_ref": None,
                "created_at": now,
                "updated_at": now,
            }

            st.session_state.metrics.append(new_metric)
            st.session_state.new_metric_submitted = new_metric

            # Persist form values for next run
            st.session_state.nm_display_name = ""
            st.session_state.nm_description = ""
            st.session_state.nm_calculation = ""
            st.session_state.nm_formula_sql = ""
            st.session_state.nm_owner_name = ""
            st.session_state.nm_owner_role = ""

            st.rerun()

# ---------------------------------------------------------------------------
# Live preview panel
# ---------------------------------------------------------------------------
with preview_col:
    st.markdown("### Live Preview")
    st.caption("Updates as you fill the form")

    # Read current form values from session state (pre-submission)
    preview_name = display_name if "display_name" in dir() else ""
    preview_domain = domain_name_selected if "domain_name_selected" in dir() else DOMAINS[0]["domain_name"]
    preview_tier = tier if "tier" in dir() else "T3"
    preview_type = metric_type if "metric_type" in dir() else "KPI"
    preview_desc = description if "description" in dir() else ""
    preview_calc = calculation if "calculation" in dir() else ""
    preview_unit = unit if "unit" in dir() else "percentage"
    preview_gran = granularity if "granularity" in dir() else "monthly"

    tier_color = {"T1": "🔴", "T2": "🟠", "T3": "⚫"}.get(preview_tier, "⚫")

    with st.container(border=True):
        st.markdown(f"## {preview_name or '*Metric name…*'}")
        st.markdown(
            f"{tier_color} **{preview_tier}** · ⚪ Draft · *{preview_domain}*"
        )
        st.markdown(f"**Type:** {preview_type.title()} · **Unit:** {preview_unit} · **Granularity:** {preview_gran.title()}")
        st.divider()
        if preview_desc:
            st.markdown("**Description**")
            st.write(preview_desc)
        else:
            st.caption("Description will appear here…")
        if preview_calc:
            st.markdown("**Business Calculation**")
            st.write(preview_calc)
        else:
            st.caption("Calculation will appear here…")

    st.divider()
    st.markdown("**Governance Tier Guide**")
    for t, info in TIER_INFO.items():
        icon = {"T1": "🔴", "T2": "🟠", "T3": "⚫"}.get(t, "")
        with st.container(border=True):
            st.markdown(f"{icon} **{t}**")
            st.caption(info)

    st.divider()
    st.markdown("**Once registered, the metric will flow through:**")
    st.markdown("""
```
Draft → Under Review → Approved
          ↓
       dbt model created
       (marts/{domain}/fct_*.sql)
          ↓
       Snowflake Semantic View
       (ANALYTICS.SEMANTIC_VIEWS.SV_*)
          ↓
       Queryable by Cortex Analyst
```
""")
