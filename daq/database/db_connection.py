from psycopg import connect, Connection, OperationalError
from psycopg_pool import ConnectionPool
from dataclasses import dataclass

@dataclass(frozen=True)
class TimescaleConfig:
    dbname: str = "daq_data"
    user: str = "fsae"
    host: str = "localhost"
    port: int = 5432

    def to_str(self) -> str:
        return f"dbname={self.dbname} user={self.user} host={self.host} port={self.port}"

DB_CONFIG = TimescaleConfig()

def get_connection() -> Connection | None:
    try:
        conn = connect(DB_CONFIG.to_str())
        #print("Connection successfully established")
        return conn
    except OperationalError as e:
        print(f'psycopg error: {e}')
        if 'Is the server running on that host and accepting TCP/IP connections?' in str(e):
            print('\nIs docker running/connected?')
        return None

def get_connection_pool(min_size: int = 1, max_size: int = 10) -> ConnectionPool | None:
    try:
        pool = ConnectionPool(DB_CONFIG.to_str(), min_size=min_size, max_size=max_size)
        #print("Connection Pool created")
        return pool
    except OperationalError as e:
        print(f'psycopg error: {e}')
        if 'Is the server running on that host and accepting TCP/IP connections?' in str(e):
            print('\nIs docker running/connected?')
        return None

def close_connection(conn: Connection | None):
    if conn is None:
        print('Connection not found')
        return

    conn.close()
    #print('Connection closed')

def test_connection() -> bool:
    print('Testing Connection ...')
    conn = get_connection()
    if conn is None:
            print('Connection failed')
            return False
        
    try:
        #print('Running SELECT 1')
        conn.execute("SELECT 1")
        close_connection(conn)
        print('Connection accessible')
        return True
    except OperationalError as e:
        print(f"psycopg error: {e}", "Connection failed")
        return False
