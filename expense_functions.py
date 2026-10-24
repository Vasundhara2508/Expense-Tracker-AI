"""
expense_functions.py - Transaction Management Business Logic

Provides CRUD operations and sample data import for the expenses table in SQLite.
Ensures strict validation on amounts, descriptions, currencies, and transaction types.
"""

import os
from pathlib import Path
import pandas as pd
from database import get_connection


def add_expense(
    date,
    description,
    amount,
    category,
    payment_method,
    transaction_type="Expense",
    currency="INR",
    category_source="Manual",
):
    """
    Inserts a new expense or income record into the SQLite database.
    Performs validation on required fields and positive amount values.
    """
    if description is None:
        raise ValueError("Description cannot be empty.")
    description = str(description).strip()
    if not description:
        raise ValueError("Description cannot be empty.")

    try:
        amount = float(amount)
    except (ValueError, TypeError):
        raise ValueError("Amount must be a valid number.")

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    if transaction_type not in ("Expense", "Income"):
        raise ValueError("Invalid transaction type. Must be 'Expense' or 'Income'.")

    if category_source not in ("Manual", "AI"):
        raise ValueError("Invalid category source. Must be 'Manual' or 'AI'.")

    if not category:
        category = "Other"

    if not payment_method:
        payment_method = "Cash"

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO expenses
            (date, description, amount, currency, transaction_type,
             category, payment_method, category_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(date),
                description,
                amount,
                currency,
                transaction_type,
                category,
                payment_method,
                category_source,
            ),
        )
        return cursor.lastrowid


def get_expenses(
    start_date=None,
    end_date=None,
    transaction_type=None,
    category=None,
    payment_method=None,
    search_query=None,
):
    """
    Retrieves expenses from SQLite, ordered by date descending.
    Supports dynamic filtering by date range, category, payment method, and search text.
    """
    query = "SELECT * FROM expenses WHERE 1=1"
    params = []

    if start_date:
        query += " AND date >= ?"
        params.append(str(start_date))

    if end_date:
        query += " AND date <= ?"
        params.append(str(end_date) + " 23:59:59" if len(str(end_date)) == 10 else str(end_date))

    if transaction_type and transaction_type != "All":
        query += " AND transaction_type = ?"
        params.append(transaction_type)

    if category and category != "All":
        query += " AND category = ?"
        params.append(category)

    if payment_method and payment_method != "All":
        query += " AND payment_method = ?"
        params.append(payment_method)

    if search_query:
        query += " AND (description LIKE ? OR category LIKE ?)"
        term = f"%{search_query.strip()}%"
        params.extend([term, term])

    query += " ORDER BY date DESC, id DESC"

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def get_expense_by_id(expense_id):
    """Retrieves a single transaction by its primary key ID."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM expenses WHERE id = ?",
            (expense_id,),
        ).fetchone()
        return dict(row) if row else None


def update_expense(
    expense_id,
    date,
    description,
    amount,
    category,
    payment_method,
    transaction_type="Expense",
    currency="INR",
):
    """Updates an existing transaction record by ID."""
    if description is None:
        raise ValueError("Description cannot be empty.")
    description = str(description).strip()
    if not description:
        raise ValueError("Description cannot be empty.")

    try:
        amount = float(amount)
    except (ValueError, TypeError):
        raise ValueError("Amount must be a valid number.")

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    if transaction_type not in ("Expense", "Income"):
        raise ValueError("Invalid transaction type.")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE expenses
            SET date = ?, description = ?, amount = ?, currency = ?,
                transaction_type = ?, category = ?, payment_method = ?,
                category_source = 'Manual'
            WHERE id = ?
            """,
            (
                str(date),
                description,
                amount,
                currency,
                transaction_type,
                category,
                payment_method,
                expense_id,
            ),
        )

        if cursor.rowcount == 0:
            raise ValueError(f"Expense with ID {expense_id} not found.")


def delete_expense(expense_id):
    """Deletes a transaction record from the database by ID."""
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM expenses WHERE id = ?",
            (expense_id,),
        )
        if cursor.rowcount == 0:
            raise ValueError(f"Expense with ID {expense_id} not found.")


def get_categories():
    """Returns a list of all distinct categories currently in the database."""
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT DISTINCT category FROM expenses ORDER BY category ASC"
        ).fetchall()
        return [row[0] for row in rows]


def get_payment_methods():
    """Returns a list of all distinct payment methods currently in the database."""
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT DISTINCT payment_method FROM expenses ORDER BY payment_method ASC"
        ).fetchall()
        return [row[0] for row in rows]


def import_sample_transactions(csv_path="data/processed/transactions_inr_only.csv"):
    """
    Safely seeds SQLite with the cleaned INR transaction dataset.
    Prevents repeated duplicates by checking existing dates and descriptions.
    Returns (imported_count, skipped_count).
    """
    if not os.path.exists(csv_path):
        # Fallback to root or sample
        alt_paths = [
            os.path.join("..", csv_path),
            "data/sample/sample_transactions.csv",
            "transactions_inr_only.csv",
        ]
        for p in alt_paths:
            if os.path.exists(p):
                csv_path = p
                break
        else:
            raise FileNotFoundError(f"Sample data file not found at {csv_path}")

    df = pd.read_csv(csv_path)

    imported_count = 0
    skipped_count = 0

    with get_connection() as conn:
        existing = conn.execute(
            "SELECT date, description, amount FROM expenses"
        ).fetchall()
        existing_keys = set((r["date"], r["description"], round(float(r["amount"]), 2)) for r in existing)

        for _, row in df.iterrows():
            date_val = str(row["date"])
            desc_val = str(row.get("description", "Unspecified expense")).strip()
            amt_val = float(row["amount"])
            key = (date_val, desc_val, round(amt_val, 2))

            if key in existing_keys:
                skipped_count += 1
                continue

            conn.execute(
                """
                INSERT INTO expenses
                (date, description, amount, currency, transaction_type,
                 category, payment_method, category_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    date_val,
                    desc_val,
                    amt_val,
                    str(row.get("currency", "INR")),
                    str(row.get("transaction_type", "Expense")),
                    str(row.get("category", "Other")),
                    str(row.get("payment_method", "Cash")),
                    "Manual",
                ),
            )
            existing_keys.add(key)
            imported_count += 1

    return imported_count, skipped_count
