"""
tests/test_analytics.py - Financial Metric Aggregation and Analytics Tests
"""

import pytest
from expense_functions import add_expense, delete_expense
from analytics import get_summary_metrics, get_category_summary, get_monthly_trend


def test_analytics_metrics_and_income_exclusion():
    # Insert known expense and income records
    id_exp = add_expense(
        date="2026-05-01 10:00:00",
        description="Analytics Test Dinner",
        amount=500.0,
        category="Food",
        payment_method="UPI / GPay / PhonePe",
        transaction_type="Expense",
    )
    id_inc = add_expense(
        date="2026-05-01 11:00:00",
        description="Analytics Test Salary",
        amount=2000.0,
        category="Income",
        payment_method="Net Banking",
        transaction_type="Income",
    )

    metrics = get_summary_metrics(start_date="2026-05-01", end_date="2026-05-01")
    assert metrics["total_expense"] == 500.0
    assert metrics["total_income"] == 2000.0
    assert metrics["net_savings"] == 1500.0

    # Ensure Category Summary STRICTLY excludes income
    cat_df = get_category_summary(start_date="2026-05-01", end_date="2026-05-01")
    assert "Income" not in cat_df["category"].values
    assert "Food" in cat_df["category"].values
    food_row = cat_df[cat_df["category"] == "Food"].iloc[0]
    assert food_row["total_amount"] == 500.0

    # Clean up
    delete_expense(id_exp)
    delete_expense(id_inc)


def test_monthly_trend_structure():
    trend_df = get_monthly_trend()
    assert hasattr(trend_df, "columns")
    for col in ["month", "expense_total", "income_total", "net_savings", "expense_count"]:
        assert col in trend_df.columns
