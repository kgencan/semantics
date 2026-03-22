"""
Shared sidebar renderer.
Injects global CSS and renders the Reset button.
Navigation is handled by Streamlit's built-in client-side sidebar nav
(rendered before any Python output — zero flicker).
"""

import streamlit as st
from utils.style import inject_global_css


def render_sidebar() -> None:
    inject_global_css()

    with st.sidebar:
        if st.button("↺  Reset Demo", type="secondary", width="stretch",
                     help="Restore all demo data to its original state"):
            from utils.reset import reset_demo
            reset_demo()
            st.rerun()
        st.caption("◈ Semantics · v0.1 · Demo mode")
