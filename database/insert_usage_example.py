import json
import sys
from pathlib import Path

try:
    from database.db_connection import close_connection, get_connection
    from database.db_insert import insert_batch, insert_single
    from parser.parser import format, parse
except ModuleNotFoundError as e:
    if e.name != 'database':
        raise

    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from database.db_connection import close_connection, get_connection
    from database.db_insert import insert_batch, insert_single
    from parser.parser import format, parse


def load_payload(path):
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)


def main():
    conn = get_connection()
    if conn is None:
        print('Could not create database connection.')
        return

    try:
        payload_a = load_payload('test_data/20220204_142345.json')
        payload_b = load_payload('test_data/20220204_142412.json')

        formatted_a = format(parse(payload_a))
        formatted_b = format(parse(payload_b))

        ok, message = insert_single(conn, formatted_a['sensors'][0])
        print('insert_single:', ok, message)

        sensor_rows = formatted_a['sensors'] + formatted_b['sensors']
        ok, message = insert_batch(conn, sensor_rows)
        print('insert_batch:', ok, message)
    finally:
        close_connection(conn)


if __name__ == '__main__':
    main()
