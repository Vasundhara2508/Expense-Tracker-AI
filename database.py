
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "expense_tracker.db"


def get_connection():
    """Create a connection to the SQLite database."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    """Create the required tables if they do not already exist."""
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL CHECK (amount > 0),
                currency TEXT NOT NULL DEFAULT 'INR',
                transaction_type TEXT NOT NULL
                    CHECK (transaction_type IN ('Expense', 'Income')),
                category TEXT NOT NULL,
                payment_method TEXT NOT NULL,
                category_source TEXT NOT NULL DEFAULT 'Manual'
                    CHECK (category_source IN ('Manual', 'AI')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month TEXT NOT NULL,
                category TEXT NOT NULL,
                budget_limit REAL NOT NULL CHECK (budget_limit > 0),
                currency TEXT NOT NULL DEFAULT 'INR',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(month, category, currency)
            )
        """)


if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized: {DB_PATH}")
