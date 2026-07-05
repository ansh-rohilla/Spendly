"""Seed realistic dummy expenses for a single user.

Usage: python seed_expense.py <user_id> <count> <months>
"""
import os
import random
import sqlite3
import sys
from datetime import date, timedelta

# Import the project's DB helper so we use the same connection pattern
# (and DB_PATH) as the rest of the app — no hardcoded filenames.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database.db import get_db  # noqa: E402

# Weighted categories — Food dominates, Health/Entertainment are rarer.
# weights sum to 100 so the "share" reads intuitively.
CATEGORY_PROFILES = {
    "Food": {
        "weight": 30,
        "min": 50, "max": 800,
        "descriptions": [
            "Weekly groceries", "Lunch with team", "Chai and samosa",
            "Dinner at restaurant", "Street food", "Breakfast at cafe",
            "Swiggy order", "Zomato order", "Snacks", "Dining out",
        ],
    },
    "Transport": {
        "weight": 18,
        "min": 20, "max": 500,
        "descriptions": [
            "Auto to office", "Uber ride", "Ola cab", "Metro recharge",
            "Petrol refill", "Rapido bike", "Bus pass top-up",
            "Train ticket", "Parking fee",
        ],
    },
    "Shopping": {
        "weight": 15,
        "min": 200, "max": 5000,
        "descriptions": [
            "Clothes", "Amazon order", "Flipkart order", "Shoes",
            "Electronics accessory", "Meesho order", "Home decor",
            "Gift for friend", "Books",
        ],
    },
    "Bills": {
        "weight": 15,
        "min": 200, "max": 3000,
        "descriptions": [
            "Electricity bill", "Mobile recharge", "Broadband bill",
            "Gas cylinder", "Water bill", "DTH recharge", "Insurance premium",
        ],
    },
    "Other": {
        "weight": 10,
        "min": 50, "max": 1000,
        "descriptions": [
            "Misc", "Household supplies", "Courier", "Donation",
            "Repair work", "Personal care",
        ],
    },
    "Health": {
        "weight": 7,
        "min": 100, "max": 2000,
        "descriptions": [
            "Pharmacy", "Doctor consultation", "Lab test", "Gym membership",
            "Health supplements", "Dental checkup",
        ],
    },
    "Entertainment": {
        "weight": 5,
        "min": 100, "max": 1500,
        "descriptions": [
            "Movie tickets", "Netflix subscription", "Spotify premium",
            "Concert ticket", "Gaming top-up", "BookMyShow",
        ],
    },
}


def pick_category():
    cats = list(CATEGORY_PROFILES.keys())
    weights = [CATEGORY_PROFILES[c]["weight"] for c in cats]
    return random.choices(cats, weights=weights, k=1)[0]


def random_date(start: date, end: date) -> date:
    delta_days = (end - start).days
    return start + timedelta(days=random.randint(0, delta_days))


def main():
    if len(sys.argv) != 4:
        print("Usage: python seed_expense.py <user_id> <count> <months>")
        sys.exit(1)

    try:
        user_id = int(sys.argv[1])
        count = int(sys.argv[2])
        months = int(sys.argv[3])
    except ValueError:
        print("All arguments must be integers.")
        sys.exit(1)

    conn = get_db()
    try:
        user = conn.execute(
            "SELECT id, name, email FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if user is None:
            print(f"No user found with id {user_id}.")
            sys.exit(1)

        today = date.today()
        earliest = today - timedelta(days=months * 30)

        rows = []
        for _ in range(count):
            category = pick_category()
            profile = CATEGORY_PROFILES[category]
            amount = round(random.uniform(profile["min"], profile["max"]), 2)
            d = random_date(earliest, today)
            description = random.choice(profile["descriptions"])
            rows.append((user_id, amount, category, d.isoformat(), description))

        # Single transaction — rollback on any failure
        try:
            conn.executemany(
                "INSERT INTO expenses (user_id, amount, category, date, description) "
                "VALUES (?, ?, ?, ?, ?)",
                rows,
            )
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Insert failed, rolled back: {e}")
            sys.exit(1)

        # Confirmation
        dates = [r[3] for r in rows]
        print(f"Inserted {len(rows)} expenses for user {user['name']} (id={user_id}).")
        print(f"Date range: {min(dates)} to {max(dates)}")
        print("\nSample of 5 inserted records:")
        sample = random.sample(rows, k=5)
        for r in sample:
            # r = (user_id, amount, category, date, description)
            print(f"  {r[3]}  ₹{r[1]:>7.2f}  {r[2]:<14}  {r[4]}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
