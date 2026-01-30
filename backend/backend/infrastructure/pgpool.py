from typing import Optional
from psycopg2.pool import SimpleConnectionPool
from infrastructure.database import get_db

_pg_pool: Optional[SimpleConnectionPool] = None

def init_pool(minconn: int, maxconn: int, dsn: str) -> None:
    """
    Initialise le pool si nécessaire. Si un pool existant est fermé, le recrée.
    """
    global _pg_pool
    if _pg_pool is None:
        _pg_pool = SimpleConnectionPool(minconn, maxconn, dsn)
        return

    # Si l'objet pool existe mais a été fermé, recréer
    try:
        if getattr(_pg_pool, "closed", False):
            _pg_pool = SimpleConnectionPool(minconn, maxconn, dsn)
    except Exception:
        # En cas d'API différente ou d'erreur, recréer le pool
        _pg_pool = SimpleConnectionPool(minconn, maxconn, dsn)

def get_pool() -> SimpleConnectionPool:
    if _pg_pool is None:
        raise RuntimeError("Connection pool non initialisé. Appeler init_pool(...) au startup.")
    return _pg_pool

def close_pool() -> None:
    """
    Ferme le pool et met la référence globale à None pour permettre une réinitialisation.
    """
    global _pg_pool
    if _pg_pool is None:
        return
    try:
        _pg_pool.closeall()
    finally:
        _pg_pool = None

def obtain_connection_from_pool():
    """
    Retourne (conn, from_pool_flag).
    from_pool_flag == True  => il faut appeler release_connection(conn, True)
    from_pool_flag == False => connexion fournie par la fixture/tests (ne pas putconn ni close)
    """


    db = get_db()
    if db is not None:
        return db.conn, False
    if _pg_pool is not None:
        return get_pool().getconn(), True

    raise RuntimeError("No pool and no test db available; init_pool(...) must be called.")

def release_connection(conn, from_pool: bool):
    if from_pool:
        try:
            get_pool().putconn(conn)
        except Exception:
            try:
                conn.close()
            except Exception:
                pass
    else:
        # connexion fournie par tests_database : ne rien faire
        return