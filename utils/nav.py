"""
Shared sidebar renderer.
Hides Streamlit's auto-generated multipage navigation and renders
the custom nav + reset button instead.
"""

import streamlit as st


def render_sidebar() -> None:
    """Inject CSS to hide the default nav, then render the custom sidebar."""

    # Hide the auto-generated Streamlit sidebar navigation
    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] { display: none; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("## ◈ Semantics")
        st.caption("Semantic Layer Governance · v0.1")
        st.divider()
        st.markdown("**Navigation**")
        st.page_link("app.py", label="Home", icon="🏠")
        st.page_link("pages/01_catalog.py", label="Metric Catalog", icon="📋")
        st.page_link("pages/02_domain_view.py", label="Domain View", icon="🏛")
        st.page_link("pages/03_new_metric.py", label="Register Metric", icon="➕")
        st.page_link("pages/04_change_requests.py", label="Change Requests", icon="📝")
        st.page_link("pages/05_reconciliation.py", label="Reconciliation", icon="⚡")
        st.page_link("pages/06_implementation_tracker.py", label="Implementation", icon="🔧")
        st.page_link("pages/07_data_dictionary.py", label="Data Dictionary", icon="📖")
        st.divider()
        if st.button("↺  Reset Demo", type="secondary", use_container_width=True,
                     help="Restore all demo data to its original state"):
            from utils.reset import reset_demo
            reset_demo()
            st.rerun()
        st.divider()
        st.caption("● Demo mode — Snowflake: ANALYTICS (emulated)")
        st.caption("dbt: last run 2026-03-12 04:31 UTC")
