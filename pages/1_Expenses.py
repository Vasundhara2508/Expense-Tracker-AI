"""
pages/1_Expenses.py - Expense Entry, AI Categorization & Transaction Management

Module 1 features styled with high-contrast executive design:
- Crisp, high-contrast labels and input fields
- Native clean card container
- Real-time AI category recommendation as user types descriptions
- Support for Expense vs Income with validation
- Filterable ledger (by Date, Category, Payment Method, Type, Search Keyword)
- Edit and Delete operations with confirmation
"""

from datetime import date, datetime
import streamlit as st
import pandas as pd
from database import initialize_database
from expense_functions import (
    add_expense,
    get_expenses,
    update_expense,
    delete_expense,
    get_expense_by_id,
    get_categories,
    get_payment_methods,
)
from ai.predict_category import predict_category
from theme import (
    apply_custom_theme,
    render_sidebar_header,
    render_sidebar_quick_stats,
    render_metric_card,
    COLOR_CARD,
    COLOR_TEXT_MUTED,
    COLOR_ACCENT_CREAM,
    COLOR_ACCENT_TERRACOTTA,
)

initialize_database()

st.set_page_config(page_title="Expenses & Transactions", page_icon="💳", layout="wide")
apply_custom_theme()
render_sidebar_header()
render_sidebar_quick_stats()

st.markdown(
    """
    <div style="margin-bottom: 1.2rem;">
        <h1 style="font-size: 2.2rem; font-weight: 800; color: #240C08; margin: 0; letter-spacing: -0.02em;">
            Expense Entry & Ledger Management
        </h1>
        <p style="font-size: 0.98rem; color: #5C3228; margin-top: 4px; font-weight: 600;">
            Record new personal expenses with instant AI category predictions, manage records, and filter your financial ledger.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

STANDARD_CATEGORIES = [
    "Food",
    "Transportation",
    "Shopping",
    "Rent",
    "Household / Utilities",
    "Entertainment",
    "Healthcare",
    "Personal Care",
    "Education",
    "Gifts",
    "Income",
    "Cashback / Rewards",
    "Transfer",
    "Other",
]

PAYMENT_METHODS = [
    "Net Banking / UPI (CUB)",
    "UPI / GPay / PhonePe",
    "Cash",
    "Credit Card",
    "Debit Card",
    "Net Banking",
    "Other",
]

tab_add, tab_manage = st.tabs(["➕ Add New Transaction", "📋 View & Filter Ledger"])

with tab_add:
    with st.container(border=True):
        st.markdown(
            """
            <div style="font-size: 1.18rem; font-weight: 800; color: #240C08; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #D6BCAB; padding-bottom: 10px;">
                <span>Record New Financial Transaction</span>
                <span style="font-size: 0.8rem; font-weight: 700; color: #8D4330; background: #EBD8CC; padding: 4px 12px; border-radius: 6px;">AI-Assisted Entry</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_type, col_date, col_amount = st.columns([1, 1, 1])
        with col_type:
            trans_type = st.radio("Transaction Type", ["Expense", "Income"], horizontal=True)
        with col_date:
            tx_date = st.date_input("Transaction Date", value=date.today())
            tx_time = st.time_input("Time", value=datetime.now().time())
        with col_amount:
            amount_val = st.number_input("Amount (INR)*", min_value=0.01, value=150.0, step=10.0, format="%.2f")

        # Description with live AI suggestion
        desc_input = st.text_input(
            "Transaction Description / Note*",
            placeholder="e.g. Swiggy biryani dinner, Metro recharge, Amazon wireless headphones, Salary from company",
            help="Type a transaction note. Our machine learning classifier will suggest the optimal category automatically.",
        )

        ai_suggestion = None
        if desc_input.strip():
            ai_res = predict_category(desc_input)
            ai_suggestion = ai_res["category"]
            conf = ai_res["confidence"]
            source = ai_res["source"]
            st.markdown(
                f"""
                <div style="background: #FAF0E8; border: 1.5px solid #D6BCAB; border-radius: 10px; padding: 10px 14px; margin: 8px 0 14px 0; color: #240C08; font-size: 0.92rem;">
                    💡 <b>AI Recommendation:</b> Suggested Category: <span style="color: #9A3822; font-weight: 800;">{ai_suggestion}</span> (Confidence: {conf*100:.1f}% via {source})
                </div>
                """,
                unsafe_allow_html=True,
            )

        col_cat, col_pay = st.columns(2)
        with col_cat:
            default_cat = ai_suggestion if (ai_suggestion and ai_suggestion in STANDARD_CATEGORIES) else ("Income" if trans_type == "Income" else "Food")
            cat_index = STANDARD_CATEGORIES.index(default_cat) if default_cat in STANDARD_CATEGORIES else 0
            selected_category = st.selectbox("Category*", STANDARD_CATEGORIES, index=cat_index)

        with col_pay:
            selected_payment = st.selectbox("Payment Method*", PAYMENT_METHODS, index=1)

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        if st.button("💾 Save Transaction", type="primary", use_container_width=True):
            if not desc_input.strip():
                st.error("Please enter a valid description for the transaction.")
            elif amount_val <= 0:
                st.error("Amount must be greater than zero.")
            else:
                full_datetime = f"{tx_date.strftime('%Y-%m-%d')} {tx_time.strftime('%H:%M:%S')}"
                category_source = "AI" if (ai_suggestion and selected_category == ai_suggestion) else "Manual"

                try:
                    new_id = add_expense(
                        date=full_datetime,
                        description=desc_input.strip(),
                        amount=amount_val,
                        category=selected_category,
                        payment_method=selected_payment,
                        transaction_type=trans_type,
                        currency="INR",
                        category_source=category_source,
                    )
                    st.success(f"Transaction #{new_id} saved successfully! ({selected_category} • ₹{amount_val:,.2f})")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to save transaction: {e}")

with tab_manage:
    with st.container(border=True):
        st.markdown(
            """
            <div style="font-size: 1.18rem; font-weight: 800; color: #240C08; margin-bottom: 16px; border-bottom: 2px solid #D6BCAB; padding-bottom: 10px;">
                Filter & Search Financial Ledger
            </div>
            """,
            unsafe_allow_html=True,
        )

        f1, f2, f3, f4, f5 = st.columns([1.2, 1.2, 1, 1, 1.2])
        with f1:
            start_d = st.date_input("From Date", value=None)
        with f2:
            end_d = st.date_input("To Date", value=None)
        with f3:
            filter_type = st.selectbox("Type", ["All", "Expense", "Income"])
        with f4:
            db_cats = ["All"] + sorted(list(set(STANDARD_CATEGORIES + get_categories())))
            filter_cat = st.selectbox("Category", db_cats)
        with f5:
            search_kw = st.text_input("Search Keyword", placeholder="Search note...")

    expenses = get_expenses(
        start_date=start_d.strftime("%Y-%m-%d") if start_d else None,
        end_date=end_d.strftime("%Y-%m-%d") if end_d else None,
        transaction_type=filter_type,
        category=filter_cat,
        search_query=search_kw,
    )

    if expenses:
        df_exp = pd.DataFrame(expenses)
        tot_exp = df_exp[df_exp["transaction_type"] == "Expense"]["amount"].sum()
        tot_inc = df_exp[df_exp["transaction_type"] == "Income"]["amount"].sum()

        st.markdown("<br>", unsafe_allow_html=True)
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown(render_metric_card("Filtered Expenses", f"₹{tot_exp:,.2f}", f"{len(df_exp[df_exp['transaction_type'] == 'Expense'])} records", "💸"), unsafe_allow_html=True)
        with sc2:
            st.markdown(render_metric_card("Filtered Income", f"₹{tot_inc:,.2f}", f"{len(df_exp[df_exp['transaction_type'] == 'Income'])} records", "💰"), unsafe_allow_html=True)
        with sc3:
            st.markdown(render_metric_card("Record Count", str(len(df_exp)), "Matching ledger items", "📋"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        display_df = df_exp[
            ["id", "date", "description", "amount", "currency", "transaction_type", "category", "payment_method", "category_source"]
        ].copy()
        display_df.columns = ["ID", "Date", "Description", "Amount (INR)", "Currency", "Type", "Category", "Payment Method", "Source"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Edit / Delete Card
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-size: 1.15rem; font-weight: 800; color: #240C08; margin-bottom: 14px; border-bottom: 2px solid #D6BCAB; padding-bottom: 8px;">
                    Modify Transaction Record
                </div>
                """,
                unsafe_allow_html=True,
            )

            c_act1, c_act2 = st.columns([1, 2])
            with c_act1:
                record_ids = df_exp["id"].tolist()
                selected_id = st.selectbox("Select Transaction ID", record_ids)

            target_row = get_expense_by_id(selected_id)

            if target_row:
                with st.form(f"edit_form_{selected_id}"):
                    e_col1, e_col2, e_col3 = st.columns(3)
                    with e_col1:
                        new_desc = st.text_input("Description", value=target_row["description"])
                        new_amt = st.number_input("Amount", value=float(target_row["amount"]), min_value=0.01)
                    with e_col2:
                        curr_date_str = str(target_row["date"])[:10]
                        try:
                            parsed_date = datetime.strptime(curr_date_str, "%Y-%m-%d").date()
                        except Exception:
                            parsed_date = date.today()
                        new_date = st.date_input("Date", value=parsed_date)
                        new_type = st.selectbox(
                            "Type", ["Expense", "Income"],
                            index=0 if target_row["transaction_type"] == "Expense" else 1
                        )
                    with e_col3:
                        cat_idx = STANDARD_CATEGORIES.index(target_row["category"]) if target_row["category"] in STANDARD_CATEGORIES else 0
                        new_cat = st.selectbox("Category", STANDARD_CATEGORIES, index=cat_idx)
                        pay_idx = PAYMENT_METHODS.index(target_row["payment_method"]) if target_row["payment_method"] in PAYMENT_METHODS else 0
                        new_pay = st.selectbox("Payment Method", PAYMENT_METHODS, index=pay_idx)

                    col_save, col_del = st.columns([1, 1])
                    with col_save:
                        save_btn = st.form_submit_button("Update Transaction", type="primary", use_container_width=True)
                    with col_del:
                        del_btn = st.form_submit_button("Delete Transaction", type="secondary", use_container_width=True)

                    if save_btn:
                        update_expense(
                            expense_id=selected_id,
                            date=f"{new_date.strftime('%Y-%m-%d')} 12:00:00",
                            description=new_desc.strip(),
                            amount=new_amt,
                            category=new_cat,
                            payment_method=new_pay,
                            transaction_type=new_type,
                            currency="INR",
                        )
                        st.success(f"Transaction #{selected_id} updated successfully!")
                        st.rerun()

                    if del_btn:
                        delete_expense(selected_id)
                        st.warning(f"Transaction #{selected_id} deleted!")
                        st.rerun()
    else:
        st.info("No records matching the filter criteria.")
