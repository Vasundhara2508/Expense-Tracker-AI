"""
pages/3_Dashboard.py - Executive Financial Analytics Dashboard

Designed matching the luxury espresso & warm cream template:
- Dark chocolate cards (#351612) with rounded borders and soft drop shadows
- Top metrics row with bold white values and currency/stat icons
- Spending Over Time trend line
- Spending by Category horizontal ranking
- Category Distribution Donut Chart
- Payment Method breakdown
- Budget Utilization Gauge
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import initialize_database
from analytics import (
    get_summary_metrics,
    get_category_summary,
    get_monthly_trend,
    get_payment_method_summary,
)
from budget_functions import calculate_budget_usage
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

st.set_page_config(page_title="Executive Dashboard", page_icon="📈", layout="wide")
apply_custom_theme()
render_sidebar_header()
render_sidebar_quick_stats()

st.markdown(
    """
    <div style="margin-bottom: 1.2rem;">
        <h1 style="font-size: 2.2rem; font-weight: 800; color: #2E120E; margin: 0; letter-spacing: -0.02em;">
            Financial Analytics Dashboard
        </h1>
        <p style="font-size: 0.98rem; color: #6D4C41; margin-top: 4px; font-weight: 500;">
            Comprehensive spending intelligence, category distributions, and compliance tracking.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Date Filter Controls
with st.container(border=True):
    f_col1, f_col2, f_col3 = st.columns([1, 1, 1.2])
    with f_col1:
        d_start = st.date_input("From Date", value=None)
    with f_col2:
        d_end = st.date_input("To Date", value=None)
    with f_col3:
        curr = st.selectbox("Currency", ["INR"])

start_iso = d_start.strftime("%Y-%m-%d") if d_start else None
end_iso = d_end.strftime("%Y-%m-%d") if d_end else None

# Data calculations
metrics = get_summary_metrics(start_date=start_iso, end_date=end_iso, currency=curr)
trend_df = get_monthly_trend(currency=curr)
df_cat = get_category_summary(start_date=start_iso, end_date=end_iso, currency=curr)
pm_df = get_payment_method_summary(start_date=start_iso, end_date=end_iso, currency=curr)

latest_month = trend_df["month"].iloc[-1] if not trend_df.empty else pd.Timestamp.now().strftime("%Y-%m")
budget_data = calculate_budget_usage(month=latest_month, currency=curr)

# 1. Top Metrics Row (5 Executive Cards matching template)
m1, m2, m3, m4, m5 = st.columns(5)

with m1:
    st.markdown(
        render_metric_card(
            label="Total Expenses",
            value=f"₹{metrics['total_expense']:,.0f}",
            subtext=f"{metrics['expense_count']} transactions",
            icon="💸",
        ),
        unsafe_allow_html=True,
    )

with m2:
    st.markdown(
        render_metric_card(
            label="Avg. Expense",
            value=f"₹{metrics['avg_expense']:,.0f}",
            subtext="Per expense record",
            icon="🏷️",
        ),
        unsafe_allow_html=True,
    )

with m3:
    st.markdown(
        render_metric_card(
            label="Total Records",
            value=f"{metrics['total_transactions']}",
            subtext=f"{metrics['income_count']} income / {metrics['expense_count']} exp",
            icon="📊",
        ),
        unsafe_allow_html=True,
    )

with m4:
    st.markdown(
        render_metric_card(
            label="Total Income",
            value=f"₹{metrics['total_income']:,.0f}",
            subtext="Credits & salary",
            icon="💰",
        ),
        unsafe_allow_html=True,
    )

with m5:
    rem_b = budget_data["total_remaining"]
    st.markdown(
        render_metric_card(
            label="Remaining Budget",
            value=f"₹{rem_b:,.0f}" if budget_data['total_budget'] > 0 else "Not Set",
            subtext=f"{budget_data['total_usage_pct']}% utilized" if budget_data['total_budget'] > 0 else f"Target: {latest_month}",
            icon="🎯",
        ),
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# 2. Main Analytics Grid (Inspired by Reference Layout)
row1_left, row1_right = st.columns([1.3, 1])

with row1_left:
    st.markdown(
        """
        <div class="espresso-card">
            <div class="espresso-card-header">
                <span>Monthly Spending & Income Trajectory</span>
                <span class="espresso-card-sub">Month-over-month trend</span>
            </div>
        """,
        unsafe_allow_html=True,
    )
    if not trend_df.empty:
        fig_trend = go.Figure()
        # Bar for Expense
        fig_trend.add_trace(go.Bar(
            x=trend_df["month"],
            y=trend_df["expense_total"],
            name="Expense",
            marker_color=COLOR_ACCENT_TERRACOTTA,
            hovertemplate="<b>%{x}</b><br>Expense: ₹%{y:,.0f}",
        ))
        # Bar for Income
        fig_trend.add_trace(go.Bar(
            x=trend_df["month"],
            y=trend_df["income_total"],
            name="Income",
            marker_color=COLOR_ACCENT_CREAM,
            hovertemplate="<b>%{x}</b><br>Income: ₹%{y:,.0f}",
        ))
        # Line for Net Savings
        fig_trend.add_trace(go.Scatter(
            x=trend_df["month"],
            y=trend_df["net_savings"],
            name="Net Balance",
            mode="lines+markers",
            line=dict(color=COLOR_ACCENT_GOLD, width=3),
            marker=dict(size=7, color="#FFFFFF"),
            hovertemplate="<b>%{x}</b><br>Net: ₹%{y:,.0f}",
        ))

        layout = get_plotly_espresso_layout()
        layout["barmode"] = "group"
        fig_trend.update_layout(layout)
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("No monthly timeline data.")
    st.markdown("</div>", unsafe_allow_html=True)

with row1_right:
    st.markdown(
        """
        <div class="espresso-card">
            <div class="espresso-card-header">
                <span>Category Distribution Share</span>
                <span class="espresso-card-sub">Expenditure breakdown</span>
            </div>
        """,
        unsafe_allow_html=True,
    )
    if not df_cat.empty:
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
        d_layout["margin"] = dict(t=20, b=20, l=20, r=20)
        fig_donut.update_layout(d_layout)
        st.plotly_chart(fig_donut, use_container_width=True)
    else:
        st.info("No category data.")
    st.markdown("</div>", unsafe_allow_html=True)

# 3. Bottom Row: Spending by Category Horizontal Ranking & Payment Breakdown + Budget Gauge
row2_col1, row2_col2, row2_col3 = st.columns([1.1, 1, 0.9])

with row2_col1:
    st.markdown(
        """
        <div class="espresso-card">
            <div class="espresso-card-header">
                <span>Top Spending Categories</span>
                <span class="espresso-card-sub">Ranked by total INR</span>
            </div>
        """,
        unsafe_allow_html=True,
    )
    if not df_cat.empty:
        df_ranked = df_cat.sort_values("total_amount", ascending=True).tail(8)
        fig_rank = px.bar(
            df_ranked,
            x="total_amount",
            y="category",
            orientation="h",
            text="total_amount",
            color="total_amount",
            color_continuous_scale=[[0, "#E8C8B5"], [0.5, "#DEAC92"], [1, "#B75D42"]],
        )
        fig_rank.update_traces(
            texttemplate="₹%{text:,.0f}",
            textposition="outside",
            textfont=dict(color="#FFFFFF", size=10),
            hovertemplate="<b>%{y}</b>: ₹%{x:,.0f}",
        )
        r_layout = get_plotly_espresso_layout()
        r_layout["coloraxis_showscale"] = False
        r_layout["xaxis"]["title_text"] = "Amount (INR)"
        r_layout["yaxis"]["title_text"] = ""
        fig_rank.update_layout(r_layout)
        st.plotly_chart(fig_rank, use_container_width=True)
    else:
        st.info("No data.")
    st.markdown("</div>", unsafe_allow_html=True)

with row2_col2:
    st.markdown(
        """
        <div class="espresso-card">
            <div class="espresso-card-header">
                <span>Payment Method Breakdown</span>
                <span class="espresso-card-sub">Channel share</span>
            </div>
        """,
        unsafe_allow_html=True,
    )
    if not pm_df.empty:
        fig_pm = px.bar(
            pm_df,
            x="payment_method",
            y="total",
            text="total",
            color="payment_method",
            color_discrete_sequence=[COLOR_ACCENT_PEACH, COLOR_ACCENT_CREAM, COLOR_ACCENT_GOLD, COLOR_ACCENT_TERRACOTTA],
        )
        fig_pm.update_traces(
            texttemplate="₹%{text:,.0f}",
            textposition="outside",
            textfont=dict(color="#FFFFFF", size=10),
        )
        pm_layout = get_plotly_espresso_layout()
        pm_layout["showlegend"] = False
        pm_layout["xaxis"]["title_text"] = ""
        pm_layout["yaxis"]["title_text"] = "Total (INR)"
        fig_pm.update_layout(pm_layout)
        st.plotly_chart(fig_pm, use_container_width=True)
    else:
        st.info("No payment method records.")
    st.markdown("</div>", unsafe_allow_html=True)

with row2_col3:
    st.markdown(
        f"""
        <div class="espresso-card">
            <div class="espresso-card-header">
                <span>Budget Gauge ({latest_month})</span>
                <span class="espresso-card-sub">Utilization</span>
            </div>
        """,
        unsafe_allow_html=True,
    )
    if budget_data["total_budget"] > 0:
        pct = budget_data["total_usage_pct"]
        bar_color = COLOR_ACCENT_CREAM if pct < 80 else (COLOR_ACCENT_GOLD if pct < 100 else COLOR_ACCENT_TERRACOTTA)

        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=budget_data["total_actual"],
            number={'prefix': "₹", 'valueformat': ",.0f", 'font': {'color': "#FFFFFF", 'size': 22}},
            gauge={
                'axis': {'range': [None, max(budget_data["total_budget"] * 1.25, budget_data["total_actual"] * 1.1)], 'tickcolor': COLOR_TEXT_MUTED},
                'bar': {'color': bar_color},
                'bgcolor': "#200B09",
                'borderwidth': 1,
                'bordercolor': "#4A1E18",
                'steps': [
                    {'range': [0, budget_data["total_budget"] * 0.8], 'color': "rgba(232, 200, 181, 0.15)"},
                    {'range': [budget_data["total_budget"] * 0.8, budget_data["total_budget"]], 'color': "rgba(217, 160, 91, 0.25)"},
                ],
                'threshold': {
                    'line': {'color': COLOR_ACCENT_TERRACOTTA, 'width': 3},
                    'thickness': 0.8,
                    'value': budget_data["total_budget"],
                },
            },
        ))
        g_layout = get_plotly_espresso_layout()
        g_layout["margin"] = dict(t=20, b=20, l=25, r=25)
        fig_g.update_layout(g_layout)
        st.plotly_chart(fig_g, use_container_width=True)
        st.markdown(
            f"""
            <div style="text-align: center; font-size: 0.82rem; color: {COLOR_TEXT_MUTED};">
                Limit: <b>₹{budget_data['total_budget']:,.0f}</b> • Used: <b>{pct}%</b>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info(f"No budget set for {latest_month}. Add limits in Module 4.")
    st.markdown("</div>", unsafe_allow_html=True)
