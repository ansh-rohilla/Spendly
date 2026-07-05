import os
import sqlite3

from werkzeug.security import generate_password_hash

# Resolve DB path relative to this file so it works no matter where the
# app is launched from.
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "spendly.db",
)


def get_db():
    """Return a SQLite connection with row_factory + FK enforcement enabled.

    Caller is responsible for closing the connection. Foreign key pragma
    is enabled on every connection because SQLite defaults to OFF.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create users and expenses tables if they do not exist.

    Safe to call multiple times — uses CREATE TABLE IF NOT EXISTS.
    """
    schema = """
    CREATE TABLE IF NOT EXISTS users (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        name          TEXT    NOT NULL,
        email         TEXT    UNIQUE NOT NULL,
        password_hash TEXT    NOT NULL,
        created_at    TEXT    DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS expenses (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER NOT NULL,
        amount      REAL    NOT NULL,
        category    TEXT    NOT NULL,
        date        TEXT    NOT NULL,
        description TEXT,
        created_at  TEXT    DEFAULT (datetime('now')),
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """
    conn = get_db()
    try:
        conn.executescript(schema)
        conn.commit()
    finally:
        conn.close()


def seed_db():
    """Insert demo user + 8 sample expenses, but only on a fresh DB.

    Idempotency: returns early if users table already has any rows.
    """
    conn = get_db()
    try:
        existing = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if existing:
            return

        # Demo user — password is "demo123", hashed with werkzeug.
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com",
             generate_password_hash("demo123", method="pbkdf2:sha256")),
        )
        user_id = conn.execute(
            "SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)
        ).fetchone()["id"]

        # 8 expenses covering all 7 spec categories; Food gets 2 entries
        # because it's the most common real-world category. Dates spread
        # across the first 5 days of July 2026 (current month per CLAUDE.md).
        expenses = [
            (user_id, 450.00,  "Food",          "2026-07-01", "Weekly groceries"),
            (user_id, 120.00,  "Food",          "2026-07-05", "Lunch with team"),
            (user_id,  60.00,  "Transport",     "2026-07-02", "Auto to office"),
            (user_id, 1500.00, "Bills",         "2026-07-03", "Electricity"),
            (user_id, 300.00,  "Health",        "2026-07-04", "Pharmacy"),
            (user_id, 600.00,  "Entertainment", "2026-07-05", "Movie tickets"),
            (user_id, 2000.00, "Shopping",      "2026-07-02", "Clothes"),
            (user_id, 100.00,  "Other",         "2026-07-05", "Misc"),
        ]
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) "
            "VALUES (?, ?, ?, ?, ?)",
            expenses,
        )
        conn.commit()
    finally:
        conn.close()
