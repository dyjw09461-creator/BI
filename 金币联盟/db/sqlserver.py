from contextlib import contextmanager

import pyodbc

from config import Config


@contextmanager
def get_connection():
    conn = pyodbc.connect(Config.connection_string())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def rows(sql, params=None):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, params or [])
        while cur.description is None and cur.nextset():
            pass
        columns = [c[0] for c in cur.description] if cur.description else []
        return [dict(zip(columns, row)) for row in cur.fetchall()]


def one(sql, params=None):
    data = rows(sql, params)
    return data[0] if data else None


def execute(sql, params=None):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, params or [])
        return cur.rowcount
