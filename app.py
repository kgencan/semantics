"""
Semantics — router.
Defines navigation, initialises session state, runs the selected page.
"""

import streamlit as st
from data.seed_data import METRICS, RECONCILIATION_LOG
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
# Navigation — section key renders as title above links (client-side, no flicker)
# ---------------------------------------------------------------------------
pg = st.navigation({
    "◈ Semantics": [
        st.Page("pages/00_home.py",                   title="Home",                   icon=":material/home:",          default=True),
        st.Page("pages/01_catalog.py",                title="Metric Catalog",         icon=":material/table_chart:"),
        st.Page("pages/02_domain_view.py",            title="Domain View",            icon=":material/account_tree:"),
        st.Page("pages/03_new_metric.py",             title="Register Metric",        icon=":material/add:"),
        st.Page("pages/04_change_requests.py",        title="Change Requests",        icon=":material/edit_note:"),
        st.Page("pages/05_reconciliation.py",         title="Reconciliation",         icon=":material/sync:"),
        st.Page("pages/06_implementation_tracker.py", title="Implementation Tracker", icon=":material/build:"),
        st.Page("pages/07_data_dictionary.py",        title="Data Dictionary",        icon=":material/book:"),
    ]
})

# ---------------------------------------------------------------------------
# Sidebar — Reset button + caption, renders below nav for every page
# ---------------------------------------------------------------------------
render_sidebar()

# ---------------------------------------------------------------------------
# Run selected page
# ---------------------------------------------------------------------------
pg.run()
