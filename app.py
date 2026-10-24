"""
app.py - AI Expense Tracker Executive Home Dashboard

Executive landing page styled with the deep espresso & warm cream template:
- Dark chocolate cards with soft drop shadows
- Executive sidebar branding and segmented quick-glance pills
- One-click sample dataset import
- Direct module cards and recent ledger overview
"""

import streamlit as st
import pandas as pd
from database import initialize_database
from expense_functions import get_expenses, import_sample_transactions
from budget_functions import get_budgets
from analytics import get_summary_metrics
from ai.predict_category import get_model
from theme import (
    apply_custom_theme,
    render_sidebar_header,
    render_sidebar_quick_stats,
    render_metric_card,
    COLOR_CARD,
    COLOR_TEXT_MUTED,
    COLOR_ACCENT_CREAM,
)

# Page configuration
st.set_page_config(
    page_title="Expense Tracker AI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database
initialize_database()

# Apply custom theme
apply_custom_theme()

# Render styled sidebar
render_sidebar_header()
metrics = get_summary_metrics(currency="INR")
active_budgets = len(get_budgets())
render_sidebar_quick_stats(metrics=metrics, active_budgets=active_budgets)

with st.sidebar:
    st.markdown("---")
    st.markdown(
        """
        <div style="padding: 10px 4px; font-size: 0.8rem; color: #D4B2A0;">
            <div style="font-weight: 700; color: #FFFFFF; margin-bottom: 4px;">SYSTEM STATUS</div>
            <div>• Database: SQLite (Connected)</div>
            <div>• ML Engine: TF-IDF + LogisticReg</div>
            <div>• Currency: INR (₹)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Top Bar / Title & Actions
t_col1, t_col2 = st.columns([3, 1.2])

with t_col1:
    st.markdown(
        """
        <div style="margin-bottom: 1.2rem;">
            <h1 style="font-size: 2.3rem; font-weight: 800; color: #240C08; margin: 0; letter-spacing: -0.02em;">
                Personal Financial Intelligence
            </h1>
            <p style="font-size: 1.02rem; color: #5C3228; margin-top: 4px; font-weight: 600;">
                AI-powered expense categorization, monthly budget compliance, and real-time interactive analytics.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with t_col2:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    if st.button("📥 Import Sample Data (INR)", use_container_width=True, help="Load 276 cleaned transactions from Dataset A"):
        imported, skipped = import_sample_transactions()
        if imported > 0:
            st.success(f"Loaded {imported} transactions ({skipped} duplicates skipped).")
            st.rerun()
        else:
            st.info(f"Database already synchronized ({skipped} records present).")

# Executive Top Metrics Row (5 Cards)
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(
        render_metric_card(
            label="Total Expenses",
            value=f"₹{metrics['total_expense']:,.0f}",
            subtext=f"{metrics['expense_count']} transactions",
            icon="💸",
        ),
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        render_metric_card(
            label="Total Income",
            value=f"₹{metrics['total_income']:,.0f}",
            subtext=f"{metrics['income_count']} transactions",
            icon="💰",
        ),
        unsafe_allow_html=True,
    )

with c3:
    net = metrics["net_savings"]
    st.markdown(
        render_metric_card(
            label="Net Balance",
            value=f"₹{net:,.0f}",
            subtext=f"{metrics['savings_rate_pct']}% savings rate",
            icon="⚖️",
        ),
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        render_metric_card(
            label="Avg. Expense",
            value=f"₹{metrics['avg_expense']:,.0f}",
            subtext="Per expense record",
            icon="🏷️",
        ),
        unsafe_allow_html=True,
    )

with c5:
    ai_ready = get_model() is not None
    st.markdown(
        render_metric_card(
            label="AI Classifier",
            value="99.6%" if ai_ready else "Rules",
            subtext="Model Accuracy (F1: 99.6%)",
            icon="🤖",
        ),
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# Navigation Module Cards
st.markdown(
    """
    <div style="font-size: 1.15rem; font-weight: 700; color: #2E120E; margin-bottom: 12px; letter-spacing: 0.02em;">
        APPLICATION MODULES
    </div>
    """,
    unsafe_allow_html=True,
)

m_c1, m_c2, m_c3, m_c4 = st.columns(4)

with m_c1:
    st.markdown(
        f"""
        <div class="espresso-card" style="margin-bottom: 0;">
            <div class="espresso-card-header">
                <span>💳 1. Expenses</span>
                <span style="font-size: 0.75rem; background: rgba(255,255,255,0.12); padding: 2px 8px; border-radius: 6px;">CRUD + AI</span>
            </div>
            <p style="font-size: 0.88rem; color: {COLOR_TEXT_MUTED}; line-height: 1.5; min-height: 65px;">
                Add personal expenses with real-time AI category suggestions. Filter and search transaction records.
            </p>
            <div style="font-size: 0.78rem; font-weight: 700; color: {COLOR_ACCENT_CREAM}; text-transform: uppercase;">
                Navigate via Sidebar →
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m_c2:
    st.markdown(
        f"""
        <div class="espresso-card" style="margin-bottom: 0;">
            <div class="espresso-card-header">
                <span>📊 2. Category Analysis</span>
                <span style="font-size: 0.75rem; background: rgba(255,255,255,0.12); padding: 2px 8px; border-radius: 6px;">Distributions</span>
            </div>
            <p style="font-size: 0.88rem; color: {COLOR_TEXT_MUTED}; line-height: 1.5; min-height: 65px;">
                Inspect spending share via donut charts, horizontal rankings, and monthly stacked category breakdowns.
            </p>
            <div style="font-size: 0.78rem; font-weight: 700; color: {COLOR_ACCENT_CREAM}; text-transform: uppercase;">
                Navigate via Sidebar →
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m_c3:
    st.markdown(
        f"""
        <div class="espresso-card" style="margin-bottom: 0;">
            <div class="espresso-card-header">
                <span>📈 3. Dashboard</span>
                <span style="font-size: 0.75rem; background: rgba(255,255,255,0.12); padding: 2px 8px; border-radius: 6px;">Plotly Visuals</span>
            </div>
            <p style="font-size: 0.88rem; color: {COLOR_TEXT_MUTED}; line-height: 1.5; min-height: 65px;">
                Comprehensive analytics with monthly trend lines, payment breakdown, and compliance utilization gauges.
            </p>
            <div style="font-size: 0.78rem; font-weight: 700; color: {COLOR_ACCENT_CREAM}; text-transform: uppercase;">
                Navigate via Sidebar →
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m_c4:
    st.markdown(
        f"""
        <div class="espresso-card" style="margin-bottom: 0;">
            <div class="espresso-card-header">
                <span>📑 4. Budgets & Reports</span>
                <span style="font-size: 0.75rem; background: rgba(255,255,255,0.12); padding: 2px 8px; border-radius: 6px;">Alerts & Export</span>
            </div>
            <p style="font-size: 0.88rem; color: {COLOR_TEXT_MUTED}; line-height: 1.5; min-height: 65px;">
                Set monthly category limits, receive threshold warnings (80% / 100%), and export CSV and Excel statements.
            </p>
            <div style="font-size: 0.78rem; font-weight: 700; color: {COLOR_ACCENT_CREAM}; text-transform: uppercase;">
                Navigate via Sidebar →
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# Recent Activity Panel
st.markdown(
    """
    <div style="font-size: 1.15rem; font-weight: 700; color: #2E120E; margin-bottom: 12px; letter-spacing: 0.02em;">
        RECENT TRANSACTIONS
    </div>
    """,
    unsafe_allow_html=True,
)

recent_tx = get_expenses()[:6]

if recent_tx:
    df_preview = pd.DataFrame(recent_tx)[
        ["id", "date", "description", "amount", "currency", "transaction_type", "category", "payment_method", "category_source"]
    ]
    df_preview.columns = ["ID", "Date", "Description", "Amount", "Currency", "Type", "Category", "Payment Method", "Source"]
    st.dataframe(df_preview, use_container_width=True, hide_index=True)
else:
    st.info("No records in the database. Click **'Import Sample Data (INR)'** in the top right to seed with your cleaned transactions.")

st.markdown("---")
st.caption("Expense Tracker AI • Python, Streamlit, SQLite & Scikit-Learn • Executive Espresso Theme")
