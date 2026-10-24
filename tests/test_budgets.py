"""
tests/test_budgets.py - Budget Management, Alerting & Threshold Tests
"""

import pytest
from expense_functions import add_expense, delete_expense
from budget_functions import (
    set_budget,
    get_budgets,
    delete_budget,
    calculate_budget_usage,
)


def test_budget_crud_and_status_alerts():
    # Set a budget limit of 1000 for 2026-06 Food
    b_id = set_budget(month="2026-06", category="Food", budget_limit=1000.0)
    assert b_id is not None

    budgets = get_budgets(month="2026-06")
    assert len(budgets) >= 1
    found = [b for b in budgets if b["category"] == "Food"][0]
    assert found["budget_limit"] == 1000.0

    # 1. Test Normal status (spending 500 / 1000 = 50%)
    exp1 = add_expense(
        date="2026-06-05 10:00:00",
        description="Normal Food Spending",
        amount=500.0,
        category="Food",
        payment_method="Cash",
    )
    usage = calculate_budget_usage(month="2026-06")
    food_budget = [b for b in usage["budgets"] if b["category"] == "Food"][0]
    assert food_budget["actual_expense"] == 500.0
    assert food_budget["usage_percentage"] == 50.0
    assert food_budget["status"] == "Normal"

    # 2. Test Warning status (spending additional 350 -> total 850 / 1000 = 85%)
    exp2 = add_expense(
        date="2026-06-10 10:00:00",
        description="Warning Threshold Food",
        amount=350.0,
        category="Food",
        payment_method="Cash",
    )
    usage_warn = calculate_budget_usage(month="2026-06")
    food_warn = [b for b in usage_warn["budgets"] if b["category"] == "Food"][0]
    assert food_warn["usage_percentage"] == 85.0
    assert food_warn["status"] == "Warning"
    assert usage_warn["has_warnings"] is True

    # 3. Test Exceeded status (spending additional 200 -> total 1050 / 1000 = 105%)
    exp3 = add_expense(
        date="2026-06-15 10:00:00",
        description="Over Limit Food",
        amount=200.0,
        category="Food",
        payment_method="Cash",
    )
    usage_exc = calculate_budget_usage(month="2026-06")
    food_exc = [b for b in usage_exc["budgets"] if b["category"] == "Food"][0]
    assert food_exc["usage_percentage"] == 105.0
    assert food_exc["status"] == "Exceeded"
    assert usage_exc["has_exceeded"] is True

    # Clean up
    delete_expense(exp1)
    delete_expense(exp2)
    delete_expense(exp3)
    delete_budget(found["id"])


def test_budget_validation():
    with pytest.raises(ValueError, match="Budget limit must be greater than zero"):
        set_budget(month="2026-06", category="Food", budget_limit=-100.0)

    with pytest.raises(ValueError, match="Month cannot be empty"):
        set_budget(month="", category="Food", budget_limit=500.0)
