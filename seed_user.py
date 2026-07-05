"""Seed a single random Indian user into Spendly's users table.

Run from the project root:
    python seed_user.py
"""

import random
import sys
from datetime import datetime

from werkzeug.security import generate_password_hash

from database.db import get_db

# Common Indian first + last names spanning North, South, East, West regions.
# Picked from frequently-used names across Hindi, Tamil, Telugu, Bengali,
# Marathi, Gujarati, Punjabi, Malayalam, and Kannada traditions.
FIRST_NAMES = [
    # North
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Reyansh", "Sai", "Arnav",
    "Ayaan", "Krishna", "Ishaan", "Shaurya", "Atharv", "Advik", "Pranav",
    # South
    "Karthik", "Arun", "Vikram", "Suresh", "Ramesh", "Pradeep", "Sandeep",
    "Manoj", "Vinay", "Rohit", "Naveen", "Sandeep", "Kiran", "Harish",
    # East / West / Central
    "Rahul", "Rohit", "Amit", "Priya", "Neha", "Pooja", "Anjali", "Sneha",
    "Ravi", "Sandeep", "Kunal", "Aakash", "Saurabh", "Nikhil", "Vikas",
    "Rakesh", "Deepak", "Manoj", "Pankaj", "Sanjay",
]

LAST_NAMES = [
    # North
    "Sharma", "Verma", "Gupta", "Agarwal", "Mishra", "Pandey", "Tiwari",
    "Saxena", "Srivastava", "Tripathi", "Singh", "Kumar", "Yadav",
    # South
    "Iyer", "Menon", "Nair", "Pillai", "Reddy", "Rao", "Naidu", "Krishnan",
    "Subramanian", "Raman", "Bhat", "Shenoy", "Kamath", "Hegde",
    # East
    "Banerjee", "Mukherjee", "Chatterjee", "Ghosh", "Das", "Bose", "Dutta",
    "Sen", "Roy", "Sarkar",
    # West
    "Patel", "Shah", "Desai", "Mehta", "Joshi", "Kulkarni", "Deshmukh",
    "Jadhav", "Pawar", "Chavan", "More", "Gaikwad",
    # Punjabi / others
    "Kaur", "Gill", "Dhillon", "Sandhu", "Bedi", "Anand",
]


def generate_user():
    """Generate a candidate user dict (name, email)."""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    name = f"{first} {last}"
    digits = random.randint(2, 3)
    suffix = f"{random.randint(10 ** (digits - 1), 10**digits - 1)}"
    email = f"{first.lower()}.{last.lower()}{suffix}@gmail.com"
    return name, email


def email_exists(conn, email):
    row = conn.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone()
    return row is not None


def main():
    conn = get_db()
    try:
        # Regenerate until we find a unique email.
        name, email = generate_user()
        attempts = 1
        while email_exists(conn, email):
            attempts += 1
            name, email = generate_user()
            if attempts > 50:
                print("Could not find a unique email after 50 attempts.", file=sys.stderr)
                sys.exit(1)

        password_hash = generate_password_hash("password123", method="pbkdf2:sha256")
        created_at = datetime.now().isoformat(sep=" ", timespec="seconds")

        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (name, email, password_hash, created_at),
        )
        conn.commit()
        user_id = cur.lastrowid

        print(f"id:    {user_id}")
        print(f"name:  {name}")
        print(f"email: {email}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
