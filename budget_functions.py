"""
budget_functions.py - Monthly Budget Management & Alerting Logic

Manages spending limits, calculates actual expenditure versus budget targets,
and determines warning/exceeded status for both overall and category-specific budgets.
"""

from database import get_connection


def set_budget(month, category, budget_limit, currency="INR"):
    """
    Sets or updates a monthly spending limit for a category or 'Overall'.
    Month must be in YYYY-MM format.
    Uses UPSERT to update existing budget if (month, category, currency) already exists.
    """
    month = str(month).strip()
    category = str(category).strip()
    if not month:
        raise ValueError("Month cannot be empty (format: YYYY-MM).")
    if not category:
        raise ValueError("Category cannot be empty.")

    try:
        budget_limit = float(budget_limit)
    except (ValueError, TypeError):
        raise ValueError("Budget limit must be a valid number.")

    if budget_limit <= 0:
        raise ValueError("Budget limit must be greater than zero.")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO budgets (month, category, budget_limit, currency)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(month, category, currency) DO UPDATE SET
                budget_limit = excluded.budget_limit
            """,
            (month, category, budget_limit, currency),
        )
        return cursor.lastrowid


def get_budgets(month=None, currency="INR"):
    """
    Retrieves all budget limits, optionally filtered by month and currency.
    """
    query = "SELECT * FROM budgets WHERE 1=1"
    params = []

    if month:
        query += " AND month = ?"
        params.append(str(month))

    if currency:
        query += " AND currency = ?"
        params.append(str(currency))

    query += " ORDER BY month DESC, category ASC"

    with get_connection() as connection:
        rows = connection.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def get_budget_by_id(budget_id):
    """Retrieves a single budget by its primary key ID."""
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM budgets WHERE id = ?",
            (budget_id,),
        ).fetchone()
        return dict(row) if row else None


def update_budget(budget_id, budget_limit):
    """Updates the limit amount of an existing budget."""
    try:
        budget_limit = float(budget_limit)
    except (ValueError, TypeError):
        raise ValueError("Budget limit must be a valid number.")

    if budget_limit <= 0:
        raise ValueError("Budget limit must be greater than zero.")

    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE budgets SET budget_limit = ? WHERE id = ?",
            (budget_limit, budget_id),
        )
        if cursor.rowcount == 0:
            raise ValueError(f"Budget with ID {budget_id} not found.")


def delete_budget(budget_id):
    """Deletes a budget limit by ID."""
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM budgets WHERE id = ?",
            (budget_id,),
        )
        if cursor.rowcount == 0:
            raise ValueError(f"Budget with ID {budget_id} not found.")


def calculate_budget_usage(month, currency="INR"):
    """
    Calculates spending versus budget for the given month (YYYY-MM).
    Returns:
    {
        "month": month,
        "budgets": [
            {
                "id": ...,
                "category": ...,
                "budget_limit": ...,
                "actual_expense": ...,
                "remaining": ...,
                "usage_percentage": ...,
                "status": "Normal" | "Warning" | "Exceeded"
            }, ...
        ],
        "total_budget": ...,
        "total_actual": ...,
        "total_remaining": ...,
        "total_usage_pct": ...,
        "has_warnings": bool,
        "has_exceeded": bool
    }
    """
    month = str(month).strip()

    with get_connection() as connection:
        # 1. Fetch budgets for this month
        budget_rows = connection.execute(
            "SELECT * FROM budgets WHERE month = ? AND currency = ?",
            (month, currency),
        ).fetchall()

        # 2. Fetch actual expenses for this month (excluding Income)
        expense_rows = connection.execute(
            """
            SELECT category, SUM(amount) as total_spent
            FROM expenses
            WHERE date LIKE ? AND transaction_type = 'Expense' AND currency = ?
            GROUP BY category
            """,
            (f"{month}%", currency),
        ).fetchall()

        # Overall actual total spent in month
        total_spent_row = connection.execute(
            """
            SELECT SUM(amount) as total_spent
            FROM expenses
            WHERE date LIKE ? AND transaction_type = 'Expense' AND currency = ?
            """,
            (f"{month}%", currency),
        ).fetchone()
        month_total_spent = float(total_spent_row["total_spent"] or 0.0)

    spent_by_category = {r["category"]: float(r["total_spent"] or 0.0) for r in expense_rows}

    budget_items = []
    overall_budget_limit = 0.0
    explicit_overall_set = False

    for b in budget_rows:
        cat = b["category"]
        limit = float(b["budget_limit"])

        if cat in ("Overall", "Total", "All"):
            actual = month_total_spent
            overall_budget_limit = limit
            explicit_overall_set = True
        else:
            actual = spent_by_category.get(cat, 0.0)
            if not explicit_overall_set:
                overall_budget_limit += limit

        remaining = limit - actual
        usage_pct = (actual / limit * 100.0) if limit > 0 else 0.0

        if usage_pct >= 100.0:
            status = "Exceeded"
        elif usage_pct >= 80.0:
            status = "Warning"
        else:
            status = "Normal"

        budget_items.append({
            "id": b["id"],
            "category": cat,
            "budget_limit": limit,
            "actual_expense": actual,
            "remaining": remaining,
            "usage_percentage": round(usage_pct, 1),
            "status": status,
        })

    # Summary calculations
    total_remaining = overall_budget_limit - month_total_spent
    total_usage_pct = (month_total_spent / overall_budget_limit * 100.0) if overall_budget_limit > 0 else 0.0

    has_warnings = any(item["status"] == "Warning" for item in budget_items)
    has_exceeded = any(item["status"] == "Exceeded" for item in budget_items)

    return {
        "month": month,
        "budgets": budget_items,
        "total_budget": round(overall_budget_limit, 2),
        "total_actual": round(month_total_spent, 2),
        "total_remaining": round(total_remaining, 2),
        "total_usage_pct": round(total_usage_pct, 1),
        "has_warnings": has_warnings,
        "has_exceeded": has_exceeded,
    }
