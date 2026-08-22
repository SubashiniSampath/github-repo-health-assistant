import os
import sqlite3
import json
from datetime import datetime, timezone

#DB_PATH = "repo_health.db"
# # This always points to the same file, no matter where you run the script from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "repo_health.db")


def get_connection():
    """Open a connection to our database file (creates it if it doesn't exist)"""
    return sqlite3.connect(DB_PATH)


def create_table():
    """Set up the table where scorecards will live, if it doesn't already exist"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scorecards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_name TEXT NOT NULL,
            scorecard_json TEXT NOT NULL,
            fetched_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_scorecard(scorecard):
    """Save one scorecard into the database"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO scorecards (repo_name, scorecard_json, fetched_at)
        VALUES (?, ?, ?)
    """, (
        scorecard["repo_name"],
        json.dumps(scorecard),
        datetime.now(timezone.utc).isoformat()
    ))

    conn.commit()
    conn.close()


def get_latest_scorecard(repo_name):
    """Get the most recently saved scorecard for a given repo, if one exists"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT scorecard_json, fetched_at FROM scorecards
        WHERE repo_name = ?
        ORDER BY fetched_at DESC
        LIMIT 1
    """, (repo_name,))

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    scorecard_json, fetched_at = row
    scorecard = json.loads(scorecard_json)
    scorecard["fetched_at"] = fetched_at
    return scorecard