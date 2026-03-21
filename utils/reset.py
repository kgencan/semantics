"""
Demo reset utility — restores all mutable session state to seed defaults.
Call reset_demo() then st.rerun() from any page.
"""

import streamlit as st


def reset_demo() -> None:
    """Reset all mutable session state to initial seed values."""
    from data.seed_data import RECONCILIATION_LOG, METRICS

    st.session_state.metrics = [dict(m) for m in METRICS]
    st.session_state.change_requests = []
    st.session_state.reconciliation_log = [dict(f) for f in RECONCILIATION_LOG]
    st.session_state.selected_metric_id = None
    st.session_state.selected_domain_id = None
    st.session_state.cr_prefill_domain = None
    st.session_state.cr_prefill_title = None
    st.session_state.cr_prefill_description = None
    st.session_state.demo_step = None


def render_reset_button() -> None:
    """Render the persistent Reset Demo button in the sidebar."""
    st.sidebar.divider()
    if st.sidebar.button("↺  Reset Demo", type="secondary", use_container_width=True, help="Restore all demo data to its original state"):
        reset_demo()
        st.rerun()
