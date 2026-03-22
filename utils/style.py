"""
CSS injection for Semantics.
Compatible with Streamlit-in-Snowflake (no external fonts, no JS, no config.toml).

All rules are scoped to [data-testid="stAppViewContainer"] so they never touch
the sidebar. This is the only way to guarantee zero sidebar flicker.

To change the color palette: edit the :root block in _CSS only.
"""

import streamlit as st

# Shorthand used throughout to scope rules away from the sidebar.
_MAIN = '[data-testid="stAppViewContainer"]'

_CSS = f"""
<style>

/* ─── COLOR VARIABLES ─────────────────────────────────────────────────────── */
:root {{
  --accent:         #446B5C;
  --accent-hover:   #325148;
  --accent-tint:    #eaf2ee;
  --bg:             #f5f6f8;
  --bg-alt:         #eceef2;
  --text-primary:   #111318;
  --text-secondary: #3d4452;
  --text-muted:     #7a8296;
  --border:         #d1d5de;
  --border-subtle:  #e4e6ed;
  --white:          #ffffff;
}}

/* ─── SHAPE RESET — main content only, never touches sidebar ─────────────── */
{_MAIN} *, {_MAIN} *::before, {_MAIN} *::after {{
    border-radius: 0px !important;
}}

/* ─── LAYOUT — tighter block container padding ───────────────────────────── */
{_MAIN} .main .block-container {{
    padding-top: 1.5rem !important;
    padding-bottom: 1.5rem !important;
    max-width: none !important;
}}

/* ─── MAIN CONTENT BACKGROUND ────────────────────────────────────────────── */
{_MAIN} > .main {{
    background-color: var(--bg);
}}

[data-testid="stHeader"] {{
    background-color: var(--bg);
    border-bottom: 1px solid var(--border);
}}

/* ─── TYPOGRAPHY — condensed, technical ──────────────────────────────────── */
{_MAIN} p, {_MAIN} li, {_MAIN} span:not([data-testid]) {{
    font-size: 13px !important;
    line-height: 1.5 !important;
}}

{_MAIN} .stCaption p, {_MAIN} .stCaption span {{
    font-size: 11px !important;
    color: var(--text-muted) !important;
}}

{_MAIN} h1 {{
    font-size: 18px !important;
    font-weight: 700 !important;
    letter-spacing: -0.01em !important;
    color: var(--text-primary) !important;
    margin-bottom: 0.15rem !important;
}}

{_MAIN} h2 {{
    font-size: 14px !important;
    font-weight: 600 !important;
    letter-spacing: 0em !important;
    color: var(--text-primary) !important;
}}

{_MAIN} h3 {{
    font-size: 13px !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
}}

{_MAIN} [data-testid="stMarkdownContainer"] label,
{_MAIN} .stTextInput label, {_MAIN} .stSelectbox label,
{_MAIN} .stTextArea label, {_MAIN} .stMultiSelect label,
{_MAIN} .stNumberInput label, {_MAIN} .stRadio label {{
    font-size: 12px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    color: var(--text-muted) !important;
}}

/* ─── DIVIDER — accent left trim ─────────────────────────────────────────── */
{_MAIN} [data-testid="stDivider"] hr {{
    border-color: var(--border-subtle) !important;
    border-top-width: 1px !important;
    margin: 0.75rem 0 !important;
}}

/* ─── SIDEBAR NAV SECTION LABEL — font size only, no layout changes ──────── */
[data-testid="stSidebarNav"] li p,
[data-testid="stSidebarNav"] [data-testid="stSidebarNavSeparator"] p {{
    font-size: 13px !important;
    font-weight: 700 !important;
    letter-spacing: 0.04em !important;
}}

/* ─── METRIC CARDS (st.metric used on other pages) ───────────────────────── */
{_MAIN} [data-testid="stMetric"] {{
    background-color: var(--white);
    border: 1px solid var(--border);
    border-top: 2px solid var(--accent) !important;
    padding: 12px 14px !important;
}}

{_MAIN} [data-testid="stMetricLabel"] p {{
    font-size: 10px !important;
    color: var(--text-muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
}}

{_MAIN} [data-testid="stMetricValue"] {{
    font-size: 22px !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
}}

{_MAIN} [data-testid="stMetricDelta"] {{
    font-size: 11px !important;
}}

/* ─── BUTTONS — main content only ────────────────────────────────────────── */
{_MAIN} .stButton > button {{
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em !important;
    padding: 4px 14px !important;
    transition: none !important;
    box-shadow: none !important;
    border-color: var(--border) !important;
}}

{_MAIN} .stButton > button[kind="primary"] {{
    background-color: var(--accent) !important;
    border-color: var(--accent) !important;
    color: var(--white) !important;
}}

{_MAIN} .stButton > button[kind="primary"]:hover {{
    background-color: var(--accent-hover) !important;
    border-color: var(--accent-hover) !important;
}}

{_MAIN} .stButton > button[kind="secondary"]:hover,
{_MAIN} .stButton > button:not([kind]):hover {{
    background-color: var(--bg-alt) !important;
    border-color: var(--text-muted) !important;
}}

{_MAIN} [data-testid="stFormSubmitButton"] > button {{
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em !important;
    padding: 4px 14px !important;
    background-color: var(--accent) !important;
    border-color: var(--accent) !important;
    color: var(--white) !important;
}}

{_MAIN} [data-testid="stFormSubmitButton"] > button:hover {{
    background-color: var(--accent-hover) !important;
    border-color: var(--accent-hover) !important;
}}

/* ─── FORM FIELDS ────────────────────────────────────────────────────────── */
{_MAIN} .stTextInput input,
{_MAIN} .stTextArea textarea,
{_MAIN} .stNumberInput input {{
    font-size: 13px !important;
    background-color: var(--white) !important;
    border-color: var(--border) !important;
}}

{_MAIN} .stTextInput input:focus,
{_MAIN} .stTextArea textarea:focus,
{_MAIN} .stNumberInput input:focus {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(68, 107, 92, 0.15) !important;
}}

{_MAIN} .stSelectbox > div > div {{
    font-size: 13px !important;
    background-color: var(--white) !important;
}}

{_MAIN} .stSelectbox > div > div:focus-within {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(68, 107, 92, 0.15) !important;
}}

{_MAIN} .stMultiSelect span[data-baseweb="tag"] {{
    font-size: 11px !important;
    background-color: var(--accent-tint) !important;
    color: var(--accent-hover) !important;
    border-color: var(--accent) !important;
}}

/* ─── DATAFRAME ──────────────────────────────────────────────────────────── */
{_MAIN} [data-testid="stDataFrame"] {{
    border: 1px solid var(--border) !important;
}}

{_MAIN} [data-testid="stDataFrame"] [role="columnheader"] {{
    font-size: 10px !important;
    font-weight: 700 !important;
    background-color: var(--bg-alt) !important;
    color: var(--text-secondary) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    border-bottom: 2px solid var(--accent) !important;
}}

{_MAIN} [data-testid="stDataFrame"] [role="gridcell"] {{
    font-size: 12px !important;
}}

/* ─── TABS ───────────────────────────────────────────────────────────────── */
{_MAIN} [data-testid="stTabs"] [role="tablist"] {{
    border-bottom: 2px solid var(--border) !important;
    gap: 0 !important;
}}

{_MAIN} [data-testid="stTabs"] [role="tab"] {{
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    padding: 6px 14px !important;
    color: var(--text-muted) !important;
}}

{_MAIN} [data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
}}

/* ─── CONTAINERS ─────────────────────────────────────────────────────────── */
{_MAIN} [data-testid="stVerticalBlockBorderWrapper"] {{
    border-color: var(--border) !important;
    background-color: var(--white) !important;
    padding: 12px 16px !important;
}}

/* ─── ALERT BOXES — override outer + inner Streamlit divs ───────────────── */
{_MAIN} [data-testid="stAlert"] {{
    border: none !important;
    border-left: 3px solid var(--accent) !important;
    background-color: var(--accent-tint) !important;
    padding: 0 !important;
}}

{_MAIN} [data-testid="stAlert"] > div {{
    background-color: var(--accent-tint) !important;
    border: none !important;
    padding: 10px 14px !important;
}}

{_MAIN} [data-testid="stAlert"] svg {{
    color: var(--accent) !important;
    fill: var(--accent) !important;
}}

{_MAIN} [data-testid="stAlert"] p {{
    font-size: 13px !important;
    color: var(--text-primary) !important;
}}

/* ─── PROGRESS BAR ───────────────────────────────────────────────────────── */
{_MAIN} [data-testid="stProgress"] [role="progressbar"] {{
    height: 6px !important;
    background-color: var(--border) !important;
}}

{_MAIN} [data-testid="stProgress"] [role="progressbar"] > div {{
    background-color: var(--accent) !important;
}}

/* ─── STATUS BADGE CLASSES (use via st.markdown HTML) ───────────────────── */
/* Usage: st.markdown('<span class="badge badge-critical">T1</span>', unsafe_allow_html=True) */
.badge {{
    display: inline-block;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 2px 6px;
    border: 1px solid currentColor;
    line-height: 1.4;
}}

.badge-critical  {{ color: #b91c1c; background: #fff0f0; border-color: #f87171; }}
.badge-warning   {{ color: #92400e; background: #fffbeb; border-color: #fbbf24; }}
.badge-ok        {{ color: #166534; background: #f0fdf4; border-color: #4ade80; }}
.badge-info      {{ color: var(--accent-hover); background: var(--accent-tint); border-color: var(--accent); }}
.badge-neutral   {{ color: var(--text-secondary); background: #f8f9fb; border-color: var(--border); }}

.badge-t1 {{ color: #b91c1c; background: #fff0f0; border-color: #f87171; }}
.badge-t2 {{ color: #92400e; background: #fffbeb; border-color: #fbbf24; }}
.badge-t3 {{ color: var(--text-secondary); background: #f8f9fb; border-color: var(--border); }}

</style>
"""


def inject_global_css() -> None:
    """Inject global CSS. Called from render_sidebar() on every page."""
    st.markdown(_CSS, unsafe_allow_html=True)
