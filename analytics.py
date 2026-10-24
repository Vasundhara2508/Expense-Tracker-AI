"""
analytics.py - Financial Calculations, Trend Aggregations & Analytical Summaries

Independent of Streamlit UI widgets to ensure testability and separation of concerns.
Provides structured metrics, category distributions, monthly comparisons, and payment breakdowns.
"""

import pandas as pd
from database import get_connection


def get_summary_metrics(start_date=None, end_date=None, currency="INR"):
    """
    Computes key performance metrics across expenses and income:
    - Total expenses (monetary sum)
    - Total income (monetary sum)
    - Net savings (Income - Expenses)
    - Total transaction counts
    - Expense count vs Income count
    - Average expense amount
    - Current month expenditure
    """
    query = """
        SELECT
            transaction_type,
            COUNT(*) as count,
            COALESCE(SUM(amount), 0.0) as total
        FROM expenses
        WHERE currency = ?
    """
    params = [currency]

    if start_date:
        query += " AND date >= ?"
        params.append(str(start_date))
    if end_date:
        query += " AND date <= ?"
        params.append(str(end_date) + " 23:59:59" if len(str(end_date)) == 10 else str(end_date))

    query += " GROUP BY transaction_type"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

        # Current month expenditure
        current_month_row = conn.execute(
            """
            SELECT COALESCE(SUM(amount), 0.0) as total
            FROM expenses
            WHERE date >= date('now', 'start of month')
              AND transaction_type = 'Expense'
              AND currency = ?
            """,
            (currency,),
        ).fetchone()

    total_expense = 0.0
    total_income = 0.0
    expense_count = 0
    income_count = 0

    for r in rows:
        t_type = r["transaction_type"]
        if t_type == "Expense":
            total_expense = float(r["total"])
            expense_count = int(r["count"])
        elif t_type == "Income":
            total_income = float(r["total"])
            income_count = int(r["count"])

    net_savings = total_income - total_expense
    avg_expense = (total_expense / expense_count) if expense_count > 0 else 0.0
    current_month_exp = float(current_month_row["total"]) if current_month_row else 0.0

    return {
        "total_expense": round(total_expense, 2),
        "total_income": round(total_income, 2),
        "net_savings": round(net_savings, 2),
        "total_transactions": expense_count + income_count,
        "expense_count": expense_count,
        "income_count": income_count,
        "avg_expense": round(avg_expense, 2),
        "current_month_expense": round(current_month_exp, 2),
        "savings_rate_pct": round((net_savings / total_income * 100), 1) if total_income > 0 else 0.0,
    }


def get_category_summary(start_date=None, end_date=None, currency="INR"):
    """
    Analyzes expense records grouped by category.
    Strictly excludes Income transactions.
    Returns a DataFrame with columns:
    [category, total_amount, transaction_count, average_amount, percentage_of_total]
    """
    query = """
        SELECT
            category,
            COUNT(*) as transaction_count,
            SUM(amount) as total_amount,
            AVG(amount) as average_amount
        FROM expenses
        WHERE transaction_type = 'Expense' AND currency = ?
    """
    params = [currency]

    if start_date:
        query += " AND date >= ?"
        params.append(str(start_date))
    if end_date:
        query += " AND date <= ?"
        params.append(str(end_date) + " 23:59:59" if len(str(end_date)) == 10 else str(end_date))

    query += " GROUP BY category ORDER BY total_amount DESC"

    with get_connection() as conn:
        df = pd.read_sql_query(query, conn, params=params)

    if df.empty:
        return pd.DataFrame(columns=["category", "total_amount", "transaction_count", "average_amount", "percentage_of_total"])

    total_sum = df["total_amount"].sum()
    df["percentage_of_total"] = (df["total_amount"] / total_sum * 100.0).round(2)
    df["total_amount"] = df["total_amount"].round(2)
    df["average_amount"] = df["average_amount"].round(2)

    return df


def get_monthly_trend(currency="INR"):
    """
    Computes month-over-month trends for both Expenses and Income.
    Returns a DataFrame sorted by month chronologically.
    Columns: [month, expense_total, income_total, net_savings, expense_count]
    """
    query = """
        SELECT
            SUBSTR(date, 1, 7) as month,
            transaction_type,
            SUM(amount) as total,
            COUNT(*) as count
        FROM expenses
        WHERE currency = ?
        GROUP BY SUBSTR(date, 1, 7), transaction_type
        ORDER BY month ASC
    """
    with get_connection() as conn:
        df_raw = pd.read_sql_query(query, conn, params=[currency])

    if df_raw.empty:
        return pd.DataFrame(columns=["month", "expense_total", "income_total", "net_savings", "expense_count"])

    # Pivot into structured monthly timeline
    months = sorted(df_raw["month"].unique())
    records = []
    for m in months:
        sub = df_raw[df_raw["month"] == m]
        exp_row = sub[sub["transaction_type"] == "Expense"]
        inc_row = sub[sub["transaction_type"] == "Income"]

        exp_tot = float(exp_row["total"].iloc[0]) if not exp_row.empty else 0.0
        inc_tot = float(inc_row["total"].iloc[0]) if not inc_row.empty else 0.0
        exp_cnt = int(exp_row["count"].iloc[0]) if not exp_row.empty else 0

        records.append({
            "month": m,
            "expense_total": round(exp_tot, 2),
            "income_total": round(inc_tot, 2),
            "net_savings": round(inc_tot - exp_tot, 2),
            "expense_count": exp_cnt,
        })

    return pd.DataFrame(records)


def get_monthly_category_breakdown(currency="INR"):
    """
    Computes category expenditure matrix across months.
    Returns a pivot DataFrame with months as rows and categories as columns.
    """
    query = """
        SELECT
            SUBSTR(date, 1, 7) as month,
            category,
            SUM(amount) as total
        FROM expenses
        WHERE transaction_type = 'Expense' AND currency = ?
        GROUP BY SUBSTR(date, 1, 7), category
        ORDER BY month ASC
    """
    with get_connection() as conn:
        df_raw = pd.read_sql_query(query, conn, params=[currency])

    if df_raw.empty:
        return pd.DataFrame()

    pivot_df = df_raw.pivot(index="month", columns="category", values="total").fillna(0.0)
    return pivot_df


def get_payment_method_summary(start_date=None, end_date=None, currency="INR"):
    """
    Calculates spending breakdown by payment method for Expense records.
    """
    query = """
        SELECT
            payment_method,
            COUNT(*) as count,
            SUM(amount) as total
        FROM expenses
        WHERE transaction_type = 'Expense' AND currency = ?
    """
    params = [currency]

    if start_date:
        query += " AND date >= ?"
        params.append(str(start_date))
    if end_date:
        query += " AND date <= ?"
        params.append(str(end_date) + " 23:59:59" if len(str(end_date)) == 10 else str(end_date))

    query += " GROUP BY payment_method ORDER BY total DESC"

    with get_connection() as conn:
        df = pd.read_sql_query(query, conn, params=params)

    if not df.empty:
        df["total"] = df["total"].round(2)
        total_sum = df["total"].sum()
        df["percentage"] = (df["total"] / total_sum * 100.0).round(2)

    return df


def get_top_categories(n=5, currency="INR"):
    """
    Identifies top N highest-spending categories and top N most frequent categories.
    """
    cat_df = get_category_summary(currency=currency)
    if cat_df.empty:
        return {"highest_spending": [], "most_frequent": []}

    highest = cat_df.sort_values("total_amount", ascending=False).head(n).to_dict("records")
    most_freq = cat_df.sort_values("transaction_count", ascending=False).head(n).to_dict("records")

    return {
        "highest_spending": highest,
        "most_frequent": most_freq,
    }
