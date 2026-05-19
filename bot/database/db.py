import os
import sqlite3
from datetime import datetime, date, timedelta

try:
    import psycopg2
    import psycopg2.extras
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

from ..config import DATABASE_URL, SQLITE_PATH


def get_connection():
    if DATABASE_URL and HAS_PSYCOPG2:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        return conn
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _is_postgres(conn):
    return hasattr(conn, "encoding")  # psycopg2 connections have this, sqlite3 doesn't


def _fetchone(conn, sql, params=()):
    cur = conn.cursor()
    cur.execute(sql, params)
    row = cur.fetchone()
    cur.close()
    if row is None:
        return None
    if _is_postgres(conn):
        return dict(row)
    return dict(row)


def _fetchall(conn, sql, params=()):
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    if _is_postgres(conn):
        return [dict(r) for r in rows]
    return [dict(r) for r in rows]


def _execute(conn, sql, params=()):
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    affected = cur.rowcount
    cur.close()
    return affected


def _insert_and_get_id(conn, sql, params=()):
    cur = conn.cursor()
    if _is_postgres(conn):
        cur.execute(sql + " RETURNING id", params)
        row_id = cur.fetchone()[0]
    else:
        cur.execute(sql, params)
        row_id = cur.lastrowid
    conn.commit()
    cur.close()
    return row_id


def init_db():
    if DATABASE_URL and HAS_PSYCOPG2:
        _init_postgres()
    else:
        _init_sqlite()


def _init_postgres():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            amount REAL NOT NULL,
            category TEXT DEFAULT 'Other',
            description TEXT DEFAULT '',
            currency TEXT DEFAULT 'PKR',
            language TEXT DEFAULT 'en',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_expenses_user_date
        ON expenses(user_id, created_at)
    """)
    conn.commit()
    cur.close()
    conn.close()


def _init_sqlite():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT DEFAULT 'Other',
            description TEXT DEFAULT '',
            currency TEXT DEFAULT 'PKR',
            language TEXT DEFAULT 'en',
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_expenses_user_date
        ON expenses(user_id, created_at)
    """)
    conn.commit()
    conn.close()


def add_expense(user_id, amount, category, description, currency="PKR", lang="en"):
    conn = get_connection()
    expense_id = _insert_and_get_id(
        conn,
        """INSERT INTO expenses (user_id, amount, category, description, currency, language)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (user_id, amount, category, description, currency, lang),
    )
    conn.close()
    return expense_id


def get_today_expenses(user_id):
    conn = get_connection()
    today = date.today().isoformat()
    rows = _fetchall(
        conn,
        """SELECT * FROM expenses
           WHERE user_id = %s AND created_at::date = %s::date
           ORDER BY created_at DESC""",
        (user_id, today),
    ) if _is_postgres(conn) else _fetchall(
        conn,
        """SELECT * FROM expenses
           WHERE user_id = ? AND date(created_at) = ?
           ORDER BY created_at DESC""",
        (user_id, today),
    )
    conn.close()
    return rows


def get_today_total(user_id):
    conn = get_connection()
    today = date.today().isoformat()
    row = _fetchone(
        conn,
        """SELECT COALESCE(SUM(amount), 0) as total
           FROM expenses
           WHERE user_id = %s AND created_at::date = %s::date""",
        (user_id, today),
    ) if _is_postgres(conn) else _fetchone(
        conn,
        """SELECT COALESCE(SUM(amount), 0) as total
           FROM expenses
           WHERE user_id = ? AND date(created_at) = ?""",
        (user_id, today),
    )
    conn.close()
    return row["total"]


def get_weekly_summary(user_id):
    conn = get_connection()
    week_ago = (date.today() - timedelta(days=7)).isoformat()
    placeholder = "%s" if _is_postgres(conn) else "?"
    rows = _fetchall(
        conn,
        f"""SELECT category, SUM(amount) as total, COUNT(*) as count
            FROM expenses
            WHERE user_id = {placeholder} AND created_at::date >= {placeholder}::date
            GROUP BY category
            ORDER BY total DESC""",
        (user_id, week_ago),
    ) if _is_postgres(conn) else _fetchall(
        conn,
        f"""SELECT category, SUM(amount) as total, COUNT(*) as count
            FROM expenses
            WHERE user_id = {placeholder} AND date(created_at) >= {placeholder}
            GROUP BY category
            ORDER BY total DESC""",
        (user_id, week_ago),
    )
    conn.close()
    return rows


def get_monthly_summary(user_id):
    conn = get_connection()
    first_of_month = date.today().replace(day=1).isoformat()
    placeholder = "%s" if _is_postgres(conn) else "?"
    rows = _fetchall(
        conn,
        f"""SELECT category, SUM(amount) as total, COUNT(*) as count
            FROM expenses
            WHERE user_id = {placeholder} AND created_at::date >= {placeholder}::date
            GROUP BY category
            ORDER BY total DESC""",
        (user_id, first_of_month),
    ) if _is_postgres(conn) else _fetchall(
        conn,
        f"""SELECT category, SUM(amount) as total, COUNT(*) as count
            FROM expenses
            WHERE user_id = {placeholder} AND date(created_at) >= {placeholder}
            GROUP BY category
            ORDER BY total DESC""",
        (user_id, first_of_month),
    )
    conn.close()
    return rows


def get_all_time_total(user_id):
    conn = get_connection()
    placeholder = "%s" if _is_postgres(conn) else "?"
    row = _fetchone(
        conn,
        f"""SELECT COALESCE(SUM(amount), 0) as total,
                   COUNT(*) as count
            FROM expenses WHERE user_id = {placeholder}""",
        (user_id,),
    )
    conn.close()
    return row["total"], row["count"]
