import json
from datetime import datetime
from parser import parse, format

SAMPLE_A = {
  "timestamp": "2022-02-04T14:24:12.456Z",
  "session_id": "auto_20220204_142000",
  "vehicle_id": "FSAE_2022_001",
  "sensors": {
    "engine_rpm": 4200,
    "throttle_position": 0.0,
    "brake_pressure": 1850.7,
    "coolant_temp": 94.1,
    "oil_pressure": 58.3,
    "intake_air_temp": 38.2,
    "battery_voltage": 13.6,
    "speed_fl": 8.5,
    "speed_fr": 8.4,
    "speed_rl": 8.6,
    "speed_rr": 8.5,
    "steering_angle": 12.8,
    "accel_lateral": -0.15,
    "accel_longitudinal": -2.45
  },
  "telemetry_metadata": {
    "packet_id": "pkt_1707058424456",
    "sample_rate_hz": 100,
    "daq_version": "v2.1.3"
  }
}

SAMPLE_B = {
  "timestamp": "2022-02-04T14:25:03.789Z",
  "session_id": "auto_20220204_142000",
  "vehicle_id": "FSAE_2022_001",
  "sensors": {
    "engine_rpm": 12800,
    "throttle_position": 100.0,
    "brake_pressure": 0.0,
    "coolant_temp": 96.8,
    "oil_pressure": 72.1,
    "intake_air_temp": 42.6,
    "battery_voltage": 13.5,
    "speed_fl": 32.1,
    "speed_fr": 32.0,
    "speed_rl": 32.3,
    "speed_rr": 32.2,
    "steering_angle": 2.1,
    "accel_lateral": 0.08,
    "accel_longitudinal": 1.87
  },
  "telemetry_metadata": {
    "packet_id": "pkt_1707058503789",
    "sample_rate_hz": 100,
    "daq_version": "v2.1.3"
  }
}

SAMPLE_C = {
  "timestamp": "2022-02-04T14:23:45.123Z",
  "session_id": "auto_20220204_142000",
  "vehicle_id": "FSAE_2022_001",
  "sensors": {
    "engine_rpm": 8500,
    "throttle_position": 87.5,
    "brake_pressure": 850.3,
    "coolant_temp": 92.3,
    "oil_pressure": 65.2,
    "intake_air_temp": 35.4,
    "battery_voltage": 13.8,
    "speed_fl": 18.2,
    "speed_fr": 18.3,
    "speed_rl": 18.1,
    "speed_rr": 18.2,
    "steering_angle": -45.2,
    "accel_lateral": 1.24,
    "accel_longitudinal": 0.85
  },
  "telemetry_metadata": {
    "packet_id": "pkt_1707058425123",
    "sample_rate_hz": 100,
    "daq_version": "v2.1.3"
  }
}

def _assert_sample_formats(sample_payload):
    parsed_payload = parse(sample_payload)
    formatted = format(parsed_payload)

    packet_row = formatted["packet"]
    sensor_rows = formatted["sensors"]

    assert isinstance(packet_row["timestamp"], datetime)
    assert packet_row["session_id"] == sample_payload["session_id"]
    assert packet_row["vehicle_id"] == sample_payload["vehicle_id"]

    assert packet_row["packet_id"] == sample_payload["telemetry_metadata"]["packet_id"]
    assert packet_row["sample_rate_hz"] == sample_payload["telemetry_metadata"]["sample_rate_hz"]
    assert packet_row["daq_version"] == sample_payload["telemetry_metadata"]["daq_version"]

    reconstructed_payload = json.loads(packet_row["raw_payload"])
    assert reconstructed_payload == sample_payload

    assert len(sensor_rows) == len(sample_payload["sensors"])
    sensor_rows_by_name = {row["sensor_name"]: row for row in sensor_rows}

    for sensor_name, expected_value in sample_payload["sensors"].items():
        assert sensor_name in sensor_rows_by_name
        row = sensor_rows_by_name[sensor_name]
        assert row["value"] == expected_value
        assert row["session_id"] == sample_payload["session_id"]
        assert row["vehicle_id"] == sample_payload["vehicle_id"]
        assert isinstance(row["timestamp"], datetime)

def test_sample_a():
    _assert_sample_formats(SAMPLE_A)

def test_sample_b():
    _assert_sample_formats(SAMPLE_B)

def test_sample_c():
    _assert_sample_formats(SAMPLE_C)

def test_parse_accepts_json_string():
    json_text = json.dumps(SAMPLE_A)
    parsed_payload = parse(json_text)
    formatted = format(parsed_payload)
    assert formatted["packet"]["session_id"] == SAMPLE_A["session_id"]
