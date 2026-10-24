"""
report_functions.py - Financial Report Generation (CSV & Excel)

Generates downloadable financial statements, transaction exports, category breakdowns,
and budget-vs-actual analysis in CSV and multi-sheet Excel (.xlsx) formats.
"""

import io
import pandas as pd
from database import get_connection
from budget_functions import calculate_budget_usage
from analytics import get_summary_metrics, get_category_summary


def export_transactions_csv(start_date=None, end_date=None, currency="INR"):
    """
    Generates a CSV export of filtered transactions.
    Returns: (csv_bytes, filename)
    """
    query = """
        SELECT
            id,
            date,
            description,
            amount,
            currency,
            transaction_type,
            category,
            payment_method,
            category_source,
            created_at
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

    query += " ORDER BY date DESC, id DESC"

    with get_connection() as conn:
        df = pd.read_sql_query(query, conn, params=params)

    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    csv_bytes = buffer.getvalue().encode("utf-8")

    filename = f"expense_tracker_export_{currency}_{start_date or 'start'}_to_{end_date or 'end'}.csv"
    return csv_bytes, filename


def export_financial_report_excel(month=None, start_date=None, end_date=None, currency="INR"):
    """
    Builds a multi-tab Excel financial workbook with:
    1. Executive Summary: Key metrics, total income, total expense, net balance.
    2. All Transactions: Full transaction ledger.
    3. Category Breakdown: Total spent, transaction count, % share.
    4. Budget vs Actual: Budget limit, actual spending, remaining, status.
    Returns: (excel_bytes, filename)
    """
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # 1. Summary Sheet
        summary = get_summary_metrics(start_date=start_date, end_date=end_date, currency=currency)
        summary_records = [
            {"Metric": "Reporting Currency", "Value": currency},
            {"Metric": "Reporting Start Date", "Value": start_date or "All Time"},
            {"Metric": "Reporting End Date", "Value": end_date or "All Time"},
            {"Metric": "Total Income", "Value": summary["total_income"]},
            {"Metric": "Total Expenses", "Value": summary["total_expense"]},
            {"Metric": "Net Savings", "Value": summary["net_savings"]},
            {"Metric": "Savings Rate (%)", "Value": f"{summary['savings_rate_pct']}%"},
            {"Metric": "Total Transactions", "Value": summary["total_transactions"]},
            {"Metric": "Expense Transaction Count", "Value": summary["expense_count"]},
            {"Metric": "Income Transaction Count", "Value": summary["income_count"]},
            {"Metric": "Average Expense Amount", "Value": summary["avg_expense"]},
        ]
        summary_df = pd.DataFrame(summary_records)
        summary_df.to_excel(writer, sheet_name="Executive Summary", index=False)

        # 2. Category Breakdown Sheet
        cat_df = get_category_summary(start_date=start_date, end_date=end_date, currency=currency)
        if cat_df.empty:
            cat_df = pd.DataFrame({"Message": ["No expense data found for selected period."]})
        cat_df.to_excel(writer, sheet_name="Category Breakdown", index=False)

        # 3. All Transactions Sheet
        query = """
            SELECT
                id as ID,
                date as Date,
                description as Description,
                amount as Amount,
                currency as Currency,
                transaction_type as Type,
                category as Category,
                payment_method as Payment_Method,
                category_source as Source
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
        query += " ORDER BY date DESC, id DESC"

        with get_connection() as conn:
            tx_df = pd.read_sql_query(query, conn, params=params)

        if tx_df.empty:
            tx_df = pd.DataFrame({"Message": ["No transactions found for selected period."]})
        tx_df.to_excel(writer, sheet_name="Transactions Ledger", index=False)

        # 4. Budget vs Actual Sheet
        target_month = month or (start_date[:7] if start_date else None)
        if target_month:
            b_usage = calculate_budget_usage(month=target_month, currency=currency)
            if b_usage["budgets"]:
                b_df = pd.DataFrame(b_usage["budgets"])
                b_df = b_df[["category", "budget_limit", "actual_expense", "remaining", "usage_percentage", "status"]]
                b_df.columns = ["Category", "Budget Limit", "Actual Expense", "Remaining", "Usage %", "Status"]
            else:
                b_df = pd.DataFrame({"Message": [f"No budget records defined for {target_month}"]})
            b_df.to_excel(writer, sheet_name="Budget vs Actual", index=False)

    excel_bytes = output.getvalue()
    filename = f"financial_report_{currency}_{month or 'all_periods'}.xlsx"
    return excel_bytes, filename
