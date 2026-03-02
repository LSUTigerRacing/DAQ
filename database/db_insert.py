from datetime import datetime

import psycopg

INSERT_SQL = """
INSERT INTO sensor_readings (timestamp, session_id, vehicle_id, sensor_name, value)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT DO NOTHING;
"""


def _to_datetime(timestamp_value):
    if isinstance(timestamp_value, datetime):
        return timestamp_value
    if isinstance(timestamp_value, str):
        iso = timestamp_value.strip()
        if iso.endswith('Z'):
            iso = iso[:-1] + '+00:00'
        return datetime.fromisoformat(iso)
    return timestamp_value


def _normalize_row(data):
    if not isinstance(data, dict):
        return None, 'Sensor data must be a dictionary.'

    required_fields = ['timestamp', 'session_id', 'vehicle_id', 'sensor_name', 'value']
    missing = [field for field in required_fields if field not in data]
    if missing:
        return None, f"Missing required field(s): {', '.join(missing)}."

    try:
        timestamp = _to_datetime(data['timestamp'])
    except Exception as e:
        return None, f'Invalid timestamp: {e}'

    if not isinstance(data['session_id'], str) or not data['session_id'].strip():
        return None, 'session_id must be a non-empty string.'
    if not isinstance(data['vehicle_id'], str) or not data['vehicle_id'].strip():
        return None, 'vehicle_id must be a non-empty string.'
    if not isinstance(data['sensor_name'], str) or not data['sensor_name'].strip():
        return None, 'sensor_name must be a non-empty string.'
    if isinstance(data['value'], bool) or not isinstance(data['value'], (int, float)):
        return None, 'value must be numeric.'

    row = (
        timestamp,
        data['session_id'],
        data['vehicle_id'],
        data['sensor_name'],
        data['value'],
    )
    return row, None


def handle_insert_error(error):
    if isinstance(error, psycopg.OperationalError):
        return False, f'Insert failed: connection error ({error})'
    if isinstance(error, psycopg.IntegrityError):
        return False, f'Insert failed: integrity error ({error})'
    if isinstance(error, psycopg.DataError):
        return False, f'Insert failed: data error ({error})'
    if isinstance(error, psycopg.DatabaseError):
        return False, f'Insert failed: database error ({error})'
    return False, f'Insert failed: {error}'


def insert_single(conn, data):
    if conn is None:
        return False, 'Insert failed: connection object is None.'

    row, error = _normalize_row(data)
    if error:
        return False, error

    try:
        with conn.cursor() as cur:
            cur.execute(INSERT_SQL, row)
            inserted_count = cur.rowcount
        conn.commit()

        if inserted_count == 1:
            return True, 'Inserted 1 sensor reading.'
        return True, 'Duplicate sensor reading skipped.'
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        return handle_insert_error(e)


def insert_batch(conn, data_list):
    if conn is None:
        return False, 'Batch insert failed: connection object is None.'
    if not isinstance(data_list, list) or not data_list:
        return False, 'Batch insert failed: data_list must be a non-empty list.'

    rows = []
    for index, data in enumerate(data_list):
        row, error = _normalize_row(data)
        if error:
            return False, f'Row {index}: {error}'
        rows.append(row)

    inserted_count = 0
    try:
        with conn.cursor() as cur:
            for row in rows:
                cur.execute(INSERT_SQL, row)
                if cur.rowcount == 1:
                    inserted_count += 1
        conn.commit()
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        return handle_insert_error(e)

    skipped_count = len(rows) - inserted_count
    return True, f'Batch insert complete: inserted {inserted_count}, skipped {skipped_count} duplicates.'
