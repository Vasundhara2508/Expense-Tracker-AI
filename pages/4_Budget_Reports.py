"""
pages/4_Budget_Reports.py - Monthly Budget Management & Downloadable Statements

Module 4 features styled with high-contrast executive design:
- Monthly category & overall spending limits
- Threshold alert monitoring (Normal <80%, Warning 80-99%, Exceeded >=100%)
- Downloadable formal reports:
  * Universal CSV Transaction Ledger
  * Multi-sheet Excel workbook (.xlsx) with 4 formatted sheets
"""

from datetime import datetime
import streamlit as st
import pandas as pd
from database import initialize_database
from budget_functions import (
    set_budget,
    get_budgets,
    delete_budget,
    calculate_budget_usage,
)
from report_functions import export_transactions_csv, export_financial_report_excel
from expense_functions import get_categories
from theme import (
    apply_custom_theme,
    render_sidebar_header,
    render_sidebar_quick_stats,
    render_metric_card,
    COLOR_CARD,
    COLOR_TEXT_MUTED,
    COLOR_ACCENT_CREAM,
    COLOR_ACCENT_TERRACOTTA,
    COLOR_ACCENT_GOLD,
)

initialize_database()

st.set_page_config(page_title="Budgets & Reports", page_icon="📑", layout="wide")
apply_custom_theme()
render_sidebar_header()
render_sidebar_quick_stats()

st.markdown(
    """
    <div style="margin-bottom: 1.2rem;">
        <h1 style="font-size: 2.2rem; font-weight: 800; color: #240C08; margin: 0; letter-spacing: -0.02em;">
            Budgets & Financial Statements
        </h1>
        <p style="font-size: 0.98rem; color: #5C3228; margin-top: 4px; font-weight: 600;">
            Define monthly spending targets, track overspending alerts, and export professional CSV/Excel financial reports.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_budget, tab_export = st.tabs(["🎯 Budget Management", "📥 Export Financial Reports"])

with tab_budget:
    with st.container(border=True):
        st.markdown(
            """
            <div style="font-size: 1.18rem; font-weight: 800; color: #240C08; margin-bottom: 16px; border-bottom: 2px solid #D6BCAB; padding-bottom: 10px;">
                Configure Monthly Spending Target
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("set_budget_form"):
            b_c1, b_c2, b_c3 = st.columns(3)
            with b_c1:
                curr_month_str = datetime.now().strftime("%Y-%m")
                b_month = st.text_input("Month (YYYY-MM)*", value=curr_month_str, help="e.g. 2022-01 or 2026-10")
            with b_c2:
                available_cats = ["Overall"] + sorted(list(set(get_categories() + ["Food", "Transportation", "Shopping", "Entertainment", "Rent", "Household / Utilities", "Healthcare", "Education"])))
                b_category = st.selectbox("Category*", available_cats)
            with b_c3:
                b_limit = st.number_input("Budget Limit (INR)*", min_value=1.0, value=5000.0, step=500.0)

            set_btn = st.form_submit_button("Save Budget Limit", type="primary", use_container_width=True)

            if set_btn:
                try:
                    set_budget(month=b_month.strip(), category=b_category, budget_limit=b_limit, currency="INR")
                    st.success(f"Budget configured! {b_category} limit for {b_month.strip()}: ₹{b_limit:,.2f}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to set budget: {e}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Review Month Performance
    all_budgets = get_budgets(currency="INR")
    distinct_months = sorted(list(set([b["month"] for b in all_budgets])), reverse=True)
    if not distinct_months:
        distinct_months = [datetime.now().strftime("%Y-%m"), "2022-01", "2022-02"]

    st.markdown(
        """
        <div style="font-size: 1.18rem; font-weight: 800; color: #240C08; margin-bottom: 10px; letter-spacing: -0.01em;">
            Monthly Compliance Audit
        </div>
        """,
        unsafe_allow_html=True,
    )
    selected_eval_month = st.selectbox("Select Target Month to Audit", distinct_months)

    usage_report = calculate_budget_usage(month=selected_eval_month, currency="INR")

    # Banner Alerts
    if usage_report["has_exceeded"]:
        st.error(f"🚨 **Budget Alert for {selected_eval_month}:** One or more categories have EXCEEDED their designated budget limits!")
    elif usage_report["has_warnings"]:
        st.warning(f"⚠️ **Budget Warning for {selected_eval_month}:** One or more categories are nearing capacity (80%+ utilized).")
    elif usage_report["total_budget"] > 0:
        st.success(f"✅ **Budget on Track:** All category expenditures are within healthy limits for {selected_eval_month}.")

    # Summary Metric Cards
    if usage_report["total_budget"] > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        ov1, ov2, ov3, ov4 = st.columns(4)
        with ov1:
            st.markdown(render_metric_card("Total Budget Limit", f"₹{usage_report['total_budget']:,.0f}", f"Target: {selected_eval_month}", "🎯"), unsafe_allow_html=True)
        with ov2:
            st.markdown(render_metric_card("Actual Total Spent", f"₹{usage_report['total_actual']:,.0f}", f"{usage_report['total_usage_pct']}% of limit", "💸"), unsafe_allow_html=True)
        with ov3:
            rem = usage_report["total_remaining"]
            st.markdown(render_metric_card("Remaining Buffer", f"₹{rem:,.0f}", "Available balance" if rem >= 0 else "Over limit", "⚖️"), unsafe_allow_html=True)
        with ov4:
            status_text = "Exceeded" if usage_report['has_exceeded'] else ("Warning" if usage_report['has_warnings'] else "Healthy")
            st.markdown(render_metric_card("Health Status", status_text, "Compliance state", "🛡️"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Category Budget Status Table
    if usage_report["budgets"]:
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-size: 1.15rem; font-weight: 800; color: #240C08; margin-bottom: 12px; border-bottom: 2px solid #D6BCAB; padding-bottom: 8px;">
                    Category Utilization Ledger
                </div>
                """,
                unsafe_allow_html=True,
            )

            b_rows = []
            for item in usage_report["budgets"]:
                b_rows.append({
                    "ID": item["id"],
                    "Category": item["category"],
                    "Budget Limit": f"₹{item['budget_limit']:,.2f}",
                    "Actual Spent": f"₹{item['actual_expense']:,.2f}",
                    "Remaining": f"₹{item['remaining']:,.2f}",
                    "Utilization %": f"{item['usage_percentage']}%",
                    "Status": item["status"],
                })

            df_b_table = pd.DataFrame(b_rows)

            def color_status(val):
                if val == "Exceeded":
                    return "color: #DC2626; font-weight: bold;"
                elif val == "Warning":
                    return "color: #D97706; font-weight: bold;"
                return "color: #059669; font-weight: bold;"

            st.dataframe(df_b_table.style.map(color_status, subset=["Status"]), use_container_width=True, hide_index=True)

            with st.expander("🗑️ Delete a Budget Limit"):
                del_id = st.selectbox("Select Budget ID to remove", [item["id"] for item in usage_report["budgets"]])
                if st.button("Confirm Delete Budget", type="secondary"):
                    delete_budget(del_id)
                    st.warning(f"Budget #{del_id} deleted.")
                    st.rerun()
    else:
        st.info(f"No budgets configured for {selected_eval_month}. Use the form above to set your first limit.")

with tab_export:
    with st.container(border=True):
        st.markdown(
            """
            <div style="font-size: 1.18rem; font-weight: 800; color: #240C08; margin-bottom: 14px; border-bottom: 2px solid #D6BCAB; padding-bottom: 10px;">
                Generate & Export Financial Statements
            </div>
            <p style="font-size: 0.90rem; color: #5C3228; font-weight: 600; margin-bottom: 16px;">
                Downloadable reports incorporate filtered transactions, separate income transfers from expenses,
                and summarize budget-vs-actual compliance.
            </p>
            """,
            unsafe_allow_html=True,
        )

        rep_col1, rep_col2, rep_col3 = st.columns([1, 1, 1])
        with rep_col1:
            exp_start = st.date_input("Report Start Date", value=None)
        with rep_col2:
            exp_end = st.date_input("Report End Date", value=None)
        with rep_col3:
            exp_month = st.text_input("Target Month (for Budget sheet)", value="2022-01")

        st_str = exp_start.strftime("%Y-%m-%d") if exp_start else None
        en_str = exp_end.strftime("%Y-%m-%d") if exp_end else None

        st.markdown("<br>", unsafe_allow_html=True)
        c_csv, c_xlsx = st.columns(2)
        with c_csv:
            st.markdown(
                """
                <div style="background: #FFFFFF; padding: 18px; border-radius: 14px; border: 1.5px solid #D6BCAB;">
                    <div style="font-weight: 800; color: #240C08; font-size: 1.05rem;">📄 Universal CSV Ledger</div>
                    <div style="font-size: 0.85rem; color: #5C3228; margin: 6px 0 16px 0; font-weight: 500;">Complete transaction ledger with timestamps, categories, and methods.</div>
                """,
                unsafe_allow_html=True,
            )
            csv_bytes, csv_filename = export_transactions_csv(start_date=st_str, end_date=en_str, currency="INR")
            st.download_button(
                label="⬇️ Download CSV Ledger",
                data=csv_bytes,
                file_name=csv_filename,
                mime="text/csv",
                type="primary",
                use_container_width=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with c_xlsx:
            st.markdown(
                """
                <div style="background: #FFFFFF; padding: 18px; border-radius: 14px; border: 1.5px solid #D6BCAB;">
                    <div style="font-weight: 800; color: #240C08; font-size: 1.05rem;">📊 Multi-Sheet Excel Workbook</div>
                    <div style="font-size: 0.85rem; color: #5C3228; margin: 6px 0 16px 0; font-weight: 500;">4 Formatted Sheets: Executive Summary, Ledger, Category, and Budgets.</div>
                """,
                unsafe_allow_html=True,
            )
            excel_bytes, excel_filename = export_financial_report_excel(
                month=exp_month.strip() if exp_month else None,
                start_date=st_str,
                end_date=en_str,
                currency="INR",
            )
            st.download_button(
                label="⬇️ Download Multi-Sheet Excel (.xlsx)",
                data=excel_bytes,
                file_name=excel_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)
