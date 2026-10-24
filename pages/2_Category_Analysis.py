"""
pages/2_Category_Analysis.py - Category Spending Intelligence

Module 2 features styled with the executive espresso design system:
- Strict exclusion of Income transfers from Expense categories
- Interactive Plotly donut chart of category distribution
- Horizontal bar chart of top spending categories
- Month-over-month stacked category breakdown
- Category summary ledger table
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from database import initialize_database
from analytics import get_category_summary, get_top_categories, get_monthly_category_breakdown
from theme import (
    apply_custom_theme,
    render_sidebar_header,
    render_sidebar_quick_stats,
    render_metric_card,
    get_plotly_espresso_layout,
    CHART_PALETTE,
    COLOR_CARD,
    COLOR_ACCENT_CREAM,
    COLOR_ACCENT_PEACH,
    COLOR_ACCENT_TERRACOTTA,
    COLOR_ACCENT_GOLD,
    COLOR_TEXT_MUTED,
)

initialize_database()

st.set_page_config(page_title="Category Analysis", page_icon="📊", layout="wide")
apply_custom_theme()
render_sidebar_header()
render_sidebar_quick_stats()

st.markdown(
    """
    <div style="margin-bottom: 1.2rem;">
        <h1 style="font-size: 2.2rem; font-weight: 800; color: #240C08; margin: 0; letter-spacing: -0.02em;">
            Expense Category Analysis
        </h1>
        <p style="font-size: 0.98rem; color: #5C3228; margin-top: 4px; font-weight: 600;">
            Where your money flows: category rankings, percentage distributions, and longitudinal category trends.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Filters Container
with st.container(border=True):
    col_f1, col_f2, col_info = st.columns([1, 1, 2])
    with col_f1:
        start_filter = st.date_input("From Date", value=None)
    with col_f2:
        end_filter = st.date_input("To Date", value=None)
    with col_info:
        st.markdown(
            """
            <div style="padding-top: 18px; font-size: 0.90rem; color: #5C3228; font-weight: 600;">
                💡 <b>Time Filter:</b> Select a date interval to isolate spending. Leaving blank analyzes your entire transaction history.
            </div>
            """,
            unsafe_allow_html=True,
        )

start_str = start_filter.strftime("%Y-%m-%d") if start_filter else None
end_str = end_filter.strftime("%Y-%m-%d") if end_filter else None

df_cat = get_category_summary(start_date=start_str, end_date=end_str, currency="INR")
top_cats = get_top_categories(currency="INR")

if df_cat.empty:
    st.warning("No expense records available for the selected period. Add transactions in '1_Expenses' or import sample data.")
else:
    highest = top_cats["highest_spending"][0] if top_cats["highest_spending"] else None
    most_freq = top_cats["most_frequent"][0] if top_cats["most_frequent"] else None
    total_spent = df_cat["total_amount"].sum()
    total_tx = df_cat["transaction_count"].sum()

    st.markdown("<br>", unsafe_allow_html=True)
    # KPI Row
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(render_metric_card("Total Period Spent", f"₹{total_spent:,.0f}", f"{len(df_cat)} distinct categories", "💸"), unsafe_allow_html=True)
    with k2:
        st.markdown(render_metric_card("Expense Transactions", f"{total_tx:,}", "Excludes income entries", "📋"), unsafe_allow_html=True)
    with k3:
        if highest:
            st.markdown(render_metric_card("Top Category", highest["category"], f"₹{highest['total_amount']:,.0f} ({highest['percentage_of_total']}%)", "🏆"), unsafe_allow_html=True)
    with k4:
        if most_freq:
            st.markdown(render_metric_card("Most Frequent", most_freq["category"], f"{most_freq['transaction_count']} transactions", "🔁"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Visualizations Row: Donut Chart & Horizontal Ranking
    c_left, c_right = st.columns([1, 1.2])

    with c_left:
        st.markdown(
            """
            <div class="espresso-card">
                <div class="espresso-card-header">
                    <span>Category Share Distribution</span>
                    <span class="espresso-card-sub">Expenditure %</span>
                </div>
            """,
            unsafe_allow_html=True,
        )
        fig_donut = px.pie(
            df_cat,
            values="total_amount",
            names="category",
            hole=0.55,
            color_discrete_sequence=CHART_PALETTE,
        )
        fig_donut.update_traces(
            textposition="outside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Amount: ₹%{value:,.0f}<br>Share: %{percent}",
            marker=dict(line=dict(color=COLOR_CARD, width=2)),
        )
        d_layout = get_plotly_espresso_layout()
        d_layout["showlegend"] = False
        d_layout["margin"] = dict(t=20, b=20, l=15, r=15)
        fig_donut.update_layout(d_layout)
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c_right:
        st.markdown(
            """
            <div class="espresso-card">
                <div class="espresso-card-header">
                    <span>Expenditure by Category (INR)</span>
                    <span class="espresso-card-sub">Volume ranking</span>
                </div>
            """,
            unsafe_allow_html=True,
        )
        df_sorted = df_cat.sort_values("total_amount", ascending=True)
        fig_bar = px.bar(
            df_sorted,
            x="total_amount",
            y="category",
            orientation="h",
            text="total_amount",
            color="total_amount",
            color_continuous_scale=[[0, "#E8C8B5"], [0.5, "#DEAC92"], [1, "#B75D42"]],
        )
        fig_bar.update_traces(
            texttemplate="₹%{text:,.0f}",
            textposition="outside",
            textfont=dict(color="#FFFFFF", size=10),
        )
        b_layout = get_plotly_espresso_layout()
        b_layout["coloraxis_showscale"] = False
        b_layout["xaxis"]["title_text"] = "Amount (INR)"
        b_layout["yaxis"]["title_text"] = ""
        fig_bar.update_layout(b_layout)
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Monthly Category Trend (Stacked)
    st.markdown(
        """
        <div class="espresso-card">
            <div class="espresso-card-header">
                <span>Month-over-Month Category Trend</span>
                <span class="espresso-card-sub">Stacked timeline comparison</span>
            </div>
        """,
        unsafe_allow_html=True,
    )
    pivot_monthly = get_monthly_category_breakdown(currency="INR")
    if not pivot_monthly.empty:
        fig_stack = px.bar(
            pivot_monthly,
            barmode="stack",
            color_discrete_sequence=CHART_PALETTE,
        )
        s_layout = get_plotly_espresso_layout()
        s_layout["xaxis"]["title_text"] = "Month"
        s_layout["yaxis"]["title_text"] = "Expenditure (INR)"
        fig_stack.update_layout(s_layout)
        st.plotly_chart(fig_stack, use_container_width=True)
    else:
        st.info("Insufficient monthly comparison data.")
    st.markdown("</div>", unsafe_allow_html=True)

    # Category Summary Table
    st.markdown(
        """
        <div style="font-size: 1.15rem; font-weight: 800; color: #240C08; margin-bottom: 12px; letter-spacing: -0.01em;">
            Category Summary Ledger
        </div>
        """,
        unsafe_allow_html=True,
    )
    display_df = df_cat.copy()
    display_df.columns = [
        "Category",
        "Total Amount (INR)",
        "Transaction Count",
        "Average per Transaction (INR)",
        "Share of Total (%)",
    ]
    st.dataframe(
        display_df.style.format({
            "Total Amount (INR)": "₹{:,.2f}",
            "Average per Transaction (INR)": "₹{:,.2f}",
            "Share of Total (%)": "{:.2f}%",
        }),
        use_container_width=True,
        hide_index=True,
    )
