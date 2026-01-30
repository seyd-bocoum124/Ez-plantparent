

class Database:
    def __init__(self, conn, commit_on_execute=True):
        self.conn = conn
        self.commit_on_execute = commit_on_execute
        self._lock = threading.Lock()

    def query(self, sql, params=None):
        cur = self.conn.cursor()
        try:
            cur.execute(sql, params or ())
            rows = cur.fetchall()
            if self.commit_on_execute:
                self.conn.commit()
            return rows
        except Exception:
            try:
                self.conn.rollback()
            except Exception:
                pass
            raise
        finally:
            cur.close()

    def query_one_dict(self, sql: str, params: tuple | None = None) -> dict | None:
        """
        Execute la requête et retourne la première ligne comme dict {colname: value}
        ou None si aucune ligne.
        """
        cur = self.conn.cursor()
        try:
            cur.execute(sql, params or ())
            row = cur.fetchone()
            if row is None:
                return None
            # cursor.description contient [(name, ...), ...]
            return {desc[0]: row[idx] for idx, desc in enumerate(cur.description)}
        except Exception:
            try:
                self.conn.rollback()
            except Exception:
                pass
            raise
        finally:
            cur.close()

    def execute(self, sql, params=None):
        with self._lock:
            with self.conn.cursor() as cur:
                cur.execute(sql, params or ())
                if self.commit_on_execute:
                    self.conn.commit()
                return cur

    def current_db_info(self):
        cur = self.conn.cursor()
        cur.execute("SELECT current_database(), inet_server_addr(), inet_server_port();")
        result = cur.fetchone()
        cur.close()
        return {"db": result[0], "host": result[1], "port": result[2]}


# infrastructure/database.py
from contextvars import ContextVar
from typing import Optional
import threading

# Context local DB (works with async + threads)
_db_var: ContextVar[Optional["Database"]] = ContextVar("db", default=None)

# Optional global fallback for code that still expects a global singleton
_global_db: Optional["Database"] = None
_global_lock = threading.Lock()

def set_db(db: Optional["Database"], *, global_fallback: bool = False) -> None:
    """
    Set the current DB in context var. If global_fallback=True also set the global fallback.
    tests_database can call set_db(db, global_fallback=True) if needed.
    """
    _db_var.set(db)
    if global_fallback:
        global _global_db
        with _global_lock:
            _global_db = db

def get_db() -> Optional["Database"]:
    """
    Return the Database for the current context, or the global fallback if set,
    or None if nothing is available. Do NOT raise here.
    """
    db = _db_var.get()
    if db is not None:
        return db
    # fallback to global if present
    global _global_db
    return _global_db