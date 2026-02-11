import psycopg
from psycopg.rows import dict_row
from psycopg import sql
from datetime import datetime
# import logging

def get_by_time_range(conn, start_time, end_time, table_name='data'):
    query = sql.SQL("SELECT * FROM {} WHERE time >= %s AND time <= %s;").format(sql.Identifier(table_name))

    try:
        with conn.cursor(row_factory=dict_row) as cur:
            times_result = cur.execute(query, (start_time, end_time)).fetchall()
            return times_result
    except Exception as e:
        print(f"Error in get_by_time_range(): {e}")
        return None


def get_sensor_reading(conn, sensor_name, timestamp, table_name='data'):
    query = sql.SQL("SELECT {} FROM {} WHERE time = %s;").format(sql.Identifier(sensor_name), sql.Identifier(table_name))
    
    try:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query, (timestamp,)) #execute expects tuple/list
            sensor_result = cur.fetchone() 

            if sensor_result:
                return sensor_result[sensor_name]
            else:
                return None
    except Exception as e:
        print(f"Error in get_sensor_reading(): {e}")
        return None

def verify_insertion(conn, timestamp, table_name='data'):
    query = sql.SQL("SELECT 1 FROM {} WHERE time = %s;").format(sql.Identifier(table_name))

    try:
        with conn.cursor() as cur:
            cur.execute(query,(timestamp)) #execute expects tuple/list
            if cur.fetchone():
                return True
    except Exception as e:
        print(f"Error in verify_insertion(): {e}")
        return False

def count_records(conn, table_name='data'):
    query = sql.SQL("SELECT COUNT(*) as total from {};").format(sql.Identifier(table_name))

    try:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query)
            record_count = cur.fetchone()
            if record_count:
                return record_count['total']

    except Exception as e:
        print(f"Error in count_records(): {e}")
        return 0
    