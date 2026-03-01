import json
from datetime import datetime

def _to_datetime(timestamp_value):
    if timestamp_value is None:
        return None
    if isinstance(timestamp_value, datetime):
        return timestamp_value
    if isinstance(timestamp_value, (int, float)):
        return datetime.fromtimestamp(timestamp_value)
    if isinstance(timestamp_value, str):
        iso = timestamp_value.strip()
        if iso.endswith("Z"):
            iso = iso[:-1] + "+00:00"
        return datetime.fromisoformat(iso)
    raise ValueError("unsupported timestamp format")

def extract_sensors(payload):
    sensor_map = payload.get("sensors")
    return sensor_map if isinstance(sensor_map, dict) else {}

def extract_metadata(payload):
    metadata_map = payload.get("telemetry_metadata")
    return metadata_map if isinstance(metadata_map, dict) else {}

def parse(json_data):
    if isinstance(json_data, str):
        payload = json.loads(json_data)
    elif isinstance(json_data, dict):
        payload = json_data
    else:
        raise ValueError("json_data must be dict or json string")

    return {
        "timestamp": _to_datetime(payload.get("timestamp")),
        "session_id": payload.get("session_id"),
        "vehicle_id": payload.get("vehicle_id"),
        "sensors": extract_sensors(payload),
        "telemetry_metadata": extract_metadata(payload),
        "raw_payload": payload,
    }

def format(parsed_payload):
    raw_payload = parsed_payload.get("raw_payload") or {}
    telemetry_metadata = parsed_payload.get("telemetry_metadata") or {}
    sensor_map = parsed_payload.get("sensors") or {}

    packet_row = {
        "timestamp": parsed_payload.get("timestamp"),
        "session_id": parsed_payload.get("session_id"),
        "vehicle_id": parsed_payload.get("vehicle_id"),
        "raw_payload": json.dumps(raw_payload, separators=(",", ":"), ensure_ascii=False),
    }

    for key, value in telemetry_metadata.items():
        packet_row[key] = value

    sensor_rows = []
    packet_timestamp = packet_row["timestamp"]
    session_id = packet_row["session_id"]
    vehicle_id = packet_row["vehicle_id"]

    for sensor_name, reading_value in sensor_map.items():
        sensor_rows.append({
            "timestamp": packet_timestamp,
            "session_id": session_id,
            "vehicle_id": vehicle_id,
            "sensor_name": sensor_name,
            "value": reading_value,
        })

    return {"packet": packet_row, "sensors": sensor_rows}
