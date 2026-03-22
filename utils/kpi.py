"""
Shared KPI card renderer.
Produces a flat, fixed-height metric card with optional inline sub-info.
"""

import streamlit as st


def kpi(col, label: str, value, sub: str = None, sub_color: str = "#7a8296",
        accent_color: str = "#446B5C") -> None:
    sub_html = (
        f'<span style="font-size:11px;color:{sub_color};padding-left:10px;font-weight:500;">{sub}</span>'
        if sub else ""
    )
    col.markdown(f"""
<div style="background:#ffffff;border:1px solid #d1d5de;border-top:2px solid {accent_color};padding:12px 14px;">
  <div style="font-size:10px;color:#7a8296;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:6px;">{label}</div>
  <div style="display:flex;align-items:center;">
    <span style="font-size:22px;font-weight:700;color:#111318;line-height:1.2;">{value}</span>{sub_html}
  </div>
</div>""", unsafe_allow_html=True)
