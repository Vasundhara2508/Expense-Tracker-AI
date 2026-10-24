"""
tests/test_database.py - Database Schema and Connection Tests
"""

import sqlite3
import pytest
from database import get_connection, initialize_database


def test_database_initialization():
    initialize_database()
    with get_connection() as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = [t[0] for t in tables]
        assert "expenses" in table_names
        assert "budgets" in table_names


def test_row_factory():
    with get_connection() as conn:
        row = conn.execute("SELECT 1 as num, 'test' as label").fetchone()
        assert row["num"] == 1
        assert row["label"] == "test"


def test_expenses_schema_constraints():
    with get_connection() as conn:
        # Invalid amount (<= 0) should fail CHECK constraint
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO expenses (date, description, amount, transaction_type, category, payment_method)
                VALUES ('2022-01-01', 'Invalid', -50, 'Expense', 'Food', 'Cash')
                """
            )
