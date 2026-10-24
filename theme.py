"""
theme.py - Shared Executive Espresso & Warm Cream Design System

High-contrast, crystal-clear styling inspired by executive financial intelligence dashboards:
- Deep chocolate-espresso cards (#351612) with heavy border-radius & soft drop shadows
- Warm cream page canvas (#EFE5DC)
- Ultra-high contrast labels (#1A0805, 100% visible, bold)
- Unified, crisp white input fields with dark espresso text and sharp borders
- Custom dark executive sidebar with segmented pill blocks & branded badges
- Cohesive Plotly chart themes (espresso background, cream/terracotta/gold palette)
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Palette tokens
COLOR_CANVAS = "#EFE5DC"
COLOR_CARD = "#351612"
COLOR_CARD_DARK = "#290F0C"
COLOR_TEXT_DARK = "#1A0805"
COLOR_TEXT_LIGHT = "#FFFFFF"
COLOR_TEXT_MUTED = "#D4B2A0"
COLOR_ACCENT_CREAM = "#E8C8B5"
COLOR_ACCENT_PEACH = "#DEAC92"
COLOR_ACCENT_TERRACOTTA = "#B75D42"
COLOR_ACCENT_GOLD = "#D9A05B"
COLOR_ACCENT_GREEN = "#5B9279"

CHART_PALETTE = [
    "#E8C8B5",  # Warm cream
    "#DEAC92",  # Blush peach
    "#D9A05B",  # Muted gold
    "#B75D42",  # Terracotta
    "#9A4430",  # Dark russet
    "#5B9279",  # Sage green
    "#7D5A50",  # Rose taupe
    "#F4D06F",  # Soft yellow
    "#E29578",  # Coral
]


def apply_custom_theme():
    """Injects comprehensive global CSS styling ensuring high contrast and clean visibility."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        /* 1. Global Font & Main Canvas */
        html, body, [class*="css"], .stApp {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
            background-color: {COLOR_CANVAS} !important;
            color: {COLOR_TEXT_DARK} !important;
        }}

        .block-container {{
            padding-top: 1.8rem;
            padding-bottom: 2.5rem;
            padding-left: 2.2rem;
            padding-right: 2.2rem;
            max-width: 96% !important;
        }}

        /* 2. Page Typography */
        h1, h2, h3, h4, h5, h6 {{
            color: #240C08 !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 800 !important;
            letter-spacing: -0.01em;
        }}

        p, span, div {{
            color: #2D1410;
        }}

        /* 3. WIDGET LABELS - FORCE MAXIMUM CONTRAST & VISIBILITY */
        label[data-testid="stWidgetLabel"],
        div[data-testid="stWidgetLabel"],
        label[data-testid="stWidgetLabel"] p,
        div[data-testid="stWidgetLabel"] p,
        div[data-testid="stWidgetLabel"] span {{
            color: #1A0805 !important;
            font-size: 0.90rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.01em !important;
            opacity: 1 !important;
            margin-bottom: 4px !important;
        }}

        /* 4. ALL FORM INPUTS (Text, Number, Date, Time, Selectbox) */
        /* Force uniform crisp white background and clear dark text */
        div[data-baseweb="input"],
        div[data-baseweb="input"] input,
        .stTextInput input,
        .stNumberInput input,
        .stDateInput input,
        .stTimeInput input,
        div[data-baseweb="select"] > div {{
            background-color: #FFFFFF !important;
            color: #1A0805 !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            border: 1.5px solid #C4A493 !important;
        }}

        /* Remove dark background override on date/time inputs */
        div[data-baseweb="input"] {{
            background-color: #FFFFFF !important;
            border: 1.5px solid #C4A493 !important;
        }}

        div[data-baseweb="input"]:focus-within,
        div[data-baseweb="select"] > div:focus-within {{
            border-color: #3E1712 !important;
            box-shadow: 0 0 0 2px rgba(62, 23, 18, 0.25) !important;
        }}

        /* Selectbox Dropdown values */
        div[data-baseweb="select"] * {{
            color: #1A0805 !important;
            font-weight: 600 !important;
        }}

        /* 5. RADIO BUTTONS */
        div[data-testid="stRadio"] label,
        div[data-testid="stRadio"] label p,
        div[data-testid="stRadio"] span {{
            color: #1A0805 !important;
            font-weight: 700 !important;
            font-size: 0.92rem !important;
            opacity: 1 !important;
        }}

        /* 6. TABS STYLING */
        button[data-baseweb="tab"] {{
            background: transparent !important;
            border-radius: 8px 8px 0 0 !important;
            padding: 10px 18px !important;
            font-weight: 700 !important;
            color: #5D372E !important;
            border-bottom: 2px solid transparent !important;
        }}

        button[data-baseweb="tab"] p {{
            color: #5D372E !important;
            font-weight: 700 !important;
            font-size: 0.95rem !important;
        }}

        button[data-baseweb="tab"][aria-selected="true"] {{
            border-bottom: 3px solid #B75D42 !important;
            background: rgba(183, 93, 66, 0.08) !important;
        }}

        button[data-baseweb="tab"][aria-selected="true"] p {{
            color: #240C08 !important;
            font-weight: 800 !important;
        }}

        /* 7. FORM & CONTAINER CARD WRAPPER */
        div[data-testid="stForm"],
        div[data-testid="stVerticalBlock"] > div[style*="border"] {{
            background-color: #FAF4EF !important;
            border: 1.5px solid #D6BCAB !important;
            border-radius: 16px !important;
            padding: 24px !important;
            box-shadow: 0 6px 18px rgba(45, 18, 14, 0.08) !important;
        }}

        /* 8. BUTTONS */
        .stButton > button[kind="primary"],
        .stButton > button:first-child,
        button[kind="primaryFormSubmit"] {{
            background: linear-gradient(135deg, {COLOR_CARD} 0%, #4A1E18 100%) !important;
            color: #FFFFFF !important;
            border: 1px solid #5C271F !important;
            border-radius: 12px !important;
            padding: 10px 24px !important;
            font-weight: 700 !important;
            letter-spacing: 0.03em !important;
            box-shadow: 0 4px 12px rgba(45, 18, 14, 0.22) !important;
            transition: all 0.2s ease !important;
        }}

        .stButton > button:hover,
        button[kind="primaryFormSubmit"]:hover {{
            background: linear-gradient(135deg, #4A1E18 0%, #5C271F 100%) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 16px rgba(45, 18, 14, 0.32) !important;
        }}

        /* 9. SIDEBAR STYLING */
        section[data-testid="stSidebar"] {{
            background-color: {COLOR_CARD_DARK} !important;
            border-right: 1px solid #4A1E18 !important;
            box-shadow: 4px 0 22px rgba(35, 12, 10, 0.35) !important;
        }}

        section[data-testid="stSidebar"] * {{
            color: #F8EDE6 !important;
        }}

        section[data-testid="stSidebar"] hr {{
            border-color: #4A1E18 !important;
            margin: 1rem 0;
        }}

        /* Sidebar Brand Box */
        .sidebar-brand-box {{
            background: linear-gradient(135deg, #4A1E18 0%, #290F0C 100%);
            border: 1px solid #5C271F;
            border-radius: 16px;
            padding: 16px 14px;
            text-align: center;
            margin-bottom: 1.2rem;
            box-shadow: inset 0 1px 2px rgba(255,255,255,0.1), 0 4px 12px rgba(0,0,0,0.3);
        }}

        .sidebar-brand-title {{
            font-size: 1.15rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #FFFFFF !important;
            margin: 0;
            line-height: 1.25;
        }}

        .sidebar-brand-sub {{
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: {COLOR_TEXT_MUTED} !important;
            margin-top: 4px;
        }}

        /* Sidebar Pills Group */
        .sidebar-pill-group {{
            background: #200B09;
            border: 1px solid #3E1611;
            border-radius: 14px;
            padding: 12px;
            margin-bottom: 1rem;
        }}

        .sidebar-pill-title {{
            font-size: 0.74rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: {COLOR_TEXT_MUTED} !important;
            margin-bottom: 8px;
        }}

        .sidebar-pill-item {{
            background: #E8D6CA;
            color: #2D120E !important;
            border-radius: 8px;
            padding: 7px 10px;
            font-size: 0.78rem;
            font-weight: 700;
            margin-bottom: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid #D6BCAB;
        }}

        .sidebar-pill-item span {{
            color: #2D120E !important;
            font-weight: 700 !important;
        }}

        /* Sidebar Nav Links */
        section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] a {{
            background: rgba(255, 255, 255, 0.04) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 10px !important;
            margin-bottom: 6px !important;
            padding: 8px 12px !important;
            transition: all 0.2s ease !important;
        }}

        section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] a:hover {{
            background: #4A1E18 !important;
            border-color: {COLOR_ACCENT_PEACH} !important;
            transform: translateX(3px);
        }}

        section[data-testid="stSidebar"] [data-testid="stSidebarNavItems"] a[aria-current="page"] {{
            background: linear-gradient(90deg, #5C271F 0%, #3F1A15 100%) !important;
            border-color: {COLOR_ACCENT_CREAM} !important;
            font-weight: 700 !important;
        }}

        /* 10. EXECUTIVE METRIC CARDS */
        .espresso-metric-card {{
            background: {COLOR_CARD};
            border: 1px solid #4A1E18;
            border-radius: 18px;
            padding: 18px 22px;
            box-shadow: 0 8px 20px rgba(45, 18, 14, 0.16);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100%;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}

        .espresso-metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 12px 28px rgba(45, 18, 14, 0.24);
        }}

        .espresso-metric-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
        }}

        .espresso-metric-label {{
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: {COLOR_TEXT_MUTED} !important;
        }}

        .espresso-metric-icon {{
            font-size: 1.1rem;
            color: {COLOR_ACCENT_CREAM} !important;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            padding: 4px 8px;
        }}

        .espresso-metric-val {{
            font-size: 1.85rem;
            font-weight: 800;
            color: #FFFFFF !important;
            letter-spacing: -0.02em;
            line-height: 1.2;
            margin-top: 2px;
        }}

        .espresso-metric-sub {{
            font-size: 0.78rem;
            font-weight: 600;
            color: {COLOR_ACCENT_PEACH} !important;
            margin-top: 6px;
        }}

        /* 11. DASHBOARD CONTAINER CARDS */
        .espresso-card {{
            background: {COLOR_CARD};
            border: 1px solid #4A1E18;
            border-radius: 20px;
            padding: 22px 24px;
            margin-bottom: 1.5rem;
            box-shadow: 0 10px 25px rgba(45, 18, 14, 0.15);
            color: #FFFFFF;
        }}

        .espresso-card-header {{
            font-size: 1.05rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            color: #FFFFFF !important;
            margin-bottom: 14px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            padding-bottom: 10px;
        }}

        .espresso-card-header * {{
            color: #FFFFFF !important;
        }}

        .espresso-card-sub {{
            font-size: 0.78rem;
            color: {COLOR_TEXT_MUTED} !important;
        }}

        /* 12. DATAFRAMES & TABLES */
        .stDataFrame {{
            border-radius: 14px !important;
            overflow: hidden !important;
            border: 1.5px solid #D6BCAB !important;
            box-shadow: 0 4px 12px rgba(45, 18, 14, 0.06) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_header():
    """Renders the executive dark chocolate sidebar panel branding."""
    with st.sidebar:
        st.markdown(
            f"""
            <div class="sidebar-brand-box">
                <div class="sidebar-brand-title">EXPENSE TRACKER</div>
                <div class="sidebar-brand-sub">Financial Intelligence AI</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_sidebar_quick_stats(metrics=None, active_budgets=0):
    """Renders sleek segmented pill stats in the sidebar matching the reference design."""
    if metrics is None:
        from analytics import get_summary_metrics
        metrics = get_summary_metrics(currency="INR")

    with st.sidebar:
        st.markdown(
            f"""
            <div class="sidebar-pill-group">
                <div class="sidebar-pill-title">Quick Glance (INR)</div>
                <div class="sidebar-pill-item">
                    <span>Expenses</span>
                    <span>₹{metrics['total_expense']:,.0f}</span>
                </div>
                <div class="sidebar-pill-item">
                    <span>Income</span>
                    <span>₹{metrics['total_income']:,.0f}</span>
                </div>
                <div class="sidebar-pill-item">
                    <span>Net Balance</span>
                    <span style="color: {'#03543F' if metrics['net_savings'] >= 0 else '#991B1B'} !important;">₹{metrics['net_savings']:,.0f}</span>
                </div>
                <div class="sidebar-pill-item">
                    <span>Transactions</span>
                    <span>{metrics['total_transactions']}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_metric_card(label, value, subtext="", icon="₹"):
    """Returns HTML string for an executive espresso metric card."""
    return f"""
    <div class="espresso-metric-card">
        <div class="espresso-metric-header">
            <span class="espresso-metric-label">{label}</span>
            <span class="espresso-metric-icon">{icon}</span>
        </div>
        <div class="espresso-metric-val">{value}</div>
        <div class="espresso-metric-sub">{subtext}</div>
    </div>
    """


def get_plotly_espresso_layout(title=""):
    """Returns a Plotly layout dictionary themed with deep espresso background and warm cream palette."""
    return dict(
        paper_bgcolor=COLOR_CARD,
        plot_bgcolor=COLOR_CARD,
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#F8EDE6"),
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(size=15, color="#FFFFFF"),
            x=0.03,
            y=0.95,
        ),
        margin=dict(t=45 if title else 25, b=25, l=35, r=25),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.08)",
            linecolor="rgba(255, 255, 255, 0.15)",
            tickfont=dict(color=COLOR_TEXT_MUTED, size=11),
            title_font=dict(color="#FFFFFF", size=12),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.08)",
            linecolor="rgba(255, 255, 255, 0.15)",
            tickfont=dict(color=COLOR_TEXT_MUTED, size=11),
            title_font=dict(color="#FFFFFF", size=12),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#F8EDE6", size=11),
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
        ),
    )
