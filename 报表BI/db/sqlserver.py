from contextlib import contextmanager

import pyodbc

from config import Config


@contextmanager
def get_connection(database=None):
    conn = pyodbc.connect(Config.connection_string(database))
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def rows(sql, params=None, database=None):
    with get_connection(database) as conn:
        cur = conn.cursor()
        cur.execute(sql, params or [])
        columns = [c[0] for c in cur.description] if cur.description else []
        return [dict(zip(columns, row)) for row in cur.fetchall()]


def one(sql, params=None, database=None):
    result = rows(sql, params, database)
    return result[0] if result else None


def execute(sql, params=None, database=None):
    with get_connection(database) as conn:
        cur = conn.cursor()
        cur.execute(sql, params or [])
        return cur.rowcount


def scalar(sql, params=None, database=None):
    with get_connection(database) as conn:
        cur = conn.cursor()
        cur.execute(sql, params or [])
        row = cur.fetchone()
        return None if row is None else row[0]


def call_with_outputs(sql, params=None):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, params or [])
        row = cur.fetchone()
        return {} if row is None else {cur.description[i][0]: row[i] for i in range(len(cur.description))}
