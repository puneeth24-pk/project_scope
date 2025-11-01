"""One-off helper: add missing columns to `projects` table.

This script imports the project's `engine` from `database.py` and runs ALTER TABLE
statements to add columns that the SQLAlchemy model expects. It is safe to run
multiple times: if a column already exists the error is caught and reported.

Run locally with:
    python scripts\add_missing_columns.py

The script uses the same DB configuration as the app (env vars or defaults in database.py).
"""
from sqlalchemy import text
from database import engine

SQLS = [
    "ALTER TABLE projects ADD COLUMN sec VARCHAR(50) NULL",
    "ALTER TABLE projects ADD COLUMN technologies VARCHAR(255) NULL",
]


def main():
    with engine.connect() as conn:
        for sql in SQLS:
            try:
                conn.execute(text(sql))
                print("OK:", sql)
            except Exception as e:
                # Print the error but continue - likely the column already exists
                print("Skipped or failed:", sql)
                print("  ->", e)


if __name__ == "__main__":
    main()
