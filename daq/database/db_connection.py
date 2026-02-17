import psycopg
import psycopg_pool
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class TimescaleConfig:
    dbname: str = "daq_data"
    user: str = "fsae"
    host: str = "localhost"
    port: int = 5432

    def to_str(self) -> str:
        return f"dbname={self.dbname} user={self.user} host={self.host} port={self.port}"

DB_CONFIG = TimescaleConfig()

def get_connection() -> psycopg.Connection | None:
    try:
        conn = psycopg.connect(DB_CONFIG.to_str())
        print("Connection successfully established")
        return conn
    except psycopg.OperationalError as e:
        print(f'psycopg error: {e}')
        if 'Is the server running on that host and accepting TCP/IP connections?' in str(e):
            print('\nIs docker running/connected?')
        return None

def get_connection_pool() -> psycopg_pool.ConnectionPool | None:
    try:
        pool = psycopg_pool.ConnectionPool(DB_CONFIG.to_str())
        print("Connection Pool created")
        return pool
    except psycopg.OperationalError as e:
        print(f'psycopg error: {e}')
        if 'Is the server running on that host and accepting TCP/IP connections?' in str(e):
            print('\nIs docker running/connected?')
        return None

def close_connection(conn: psycopg.Connection | None):
    if conn is None:
        print('Connection not found')
        return
    conn.close()
    print('Connection closed')

def test_connection() -> bool:
    print('Establishing Connection')
    conn = get_connection()
    if conn is None:
            print('Connection failed')
            return False
    try:
        print('Running SELECT 1')
        conn.execute("SELECT 1")
        close_connection(conn)
        print('Connection accessible')
        return True
    except psycopg.Error as e:
        print(f"psycopg error: {e}", "Connection failed")
        return False
