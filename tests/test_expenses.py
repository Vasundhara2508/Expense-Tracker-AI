"""
tests/test_expenses.py - CRUD Operations and Input Validation Tests
"""

import pytest
from expense_functions import (
    add_expense,
    get_expenses,
    get_expense_by_id,
    update_expense,
    delete_expense,
)


def test_add_and_get_expense():
    new_id = add_expense(
        date="2026-01-15 10:00:00",
        description="Test Cafe Coffee",
        amount=180.50,
        category="Food",
        payment_method="UPI / GPay / PhonePe",
        transaction_type="Expense",
    )
    assert new_id is not None
    assert new_id > 0

    record = get_expense_by_id(new_id)
    assert record is not None
    assert record["description"] == "Test Cafe Coffee"
    assert record["amount"] == 180.50
    assert record["category"] == "Food"
    assert record["transaction_type"] == "Expense"

    # Clean up
    delete_expense(new_id)


def test_update_expense():
    new_id = add_expense(
        date="2026-01-16 12:00:00",
        description="Original Grocery Item",
        amount=300.0,
        category="Food",
        payment_method="Cash",
    )

    update_expense(
        expense_id=new_id,
        date="2026-01-16 13:00:00",
        description="Updated Grocery Supermarket",
        amount=350.0,
        category="Shopping",
        payment_method="Debit Card",
        transaction_type="Expense",
    )

    updated = get_expense_by_id(new_id)
    assert updated["description"] == "Updated Grocery Supermarket"
    assert updated["amount"] == 350.0
    assert updated["category"] == "Shopping"

    delete_expense(new_id)


def test_delete_expense():
    new_id = add_expense(
        date="2026-01-17 14:00:00",
        description="Temp Item for Deletion",
        amount=50.0,
        category="Other",
        payment_method="Cash",
    )
    delete_expense(new_id)
    assert get_expense_by_id(new_id) is None


def test_validation_errors():
    # Empty description
    with pytest.raises(ValueError, match="Description cannot be empty"):
        add_expense(
            date="2026-01-18",
            description="   ",
            amount=100.0,
            category="Food",
            payment_method="Cash",
        )

    # Non-positive amount
    with pytest.raises(ValueError, match="Amount must be greater than zero"):
        add_expense(
            date="2026-01-18",
            description="Test Zero",
            amount=0.0,
            category="Food",
            payment_method="Cash",
        )

    # Invalid transaction type
    with pytest.raises(ValueError, match="Invalid transaction type"):
        add_expense(
            date="2026-01-18",
            description="Test Invalid Type",
            amount=100.0,
            category="Food",
            payment_method="Cash",
            transaction_type="Donation",
        )
