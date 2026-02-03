import psycopg2
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
from .config import settings

pool: SimpleConnectionPool | None = None

def init_pool():
    global pool
    if pool is None:
        pool = SimpleConnectionPool(minconn=1, maxconn=10, dsn=settings.postgres_url)

@contextmanager
def get_conn():
    if pool is None:
        init_pool()
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)

def close_pool():
    global pool
    if pool:
        pool.closeall()
        pool = None