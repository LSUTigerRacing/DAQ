"""
Unit tests for the Formula SAE Telemetry JSON Validator Module
"""

import unittest
from validator import (
    validate_payload,
    validate_sensors,
    validate_metadata,
    validate_timestamp,
)


class TestValidateTimestamp(unittest.TestCase):
    """Test cases for timestamp validation"""

    def test_valid_iso8601_timestamp(self):
        """Test valid ISO 8601 timestamps"""
        valid_timestamps = [
            "2024-01-15T10:30:00Z",
            "2024-01-15T10:30:00+00:00",
            "2024-01-15T10:30:00.123456Z",
            "2024-12-31T23:59:59Z",
        ]
        for ts in valid_timestamps:
            is_valid, error = validate_timestamp(ts)
            self.assertTrue(is_valid, f"Timestamp {ts} should be valid")
            self.assertEqual(error, "")

    def test_invalid_timestamp_format(self):
        """Test invalid timestamp formats"""
        invalid_timestamps = [
            "2024-01-15",           # Missing time
            "10:30:00",             # Missing date
            "2024/01/15 10:30:00",  # Wrong separator
            "not-a-timestamp",
        ]
        for ts in invalid_timestamps:
            is_valid, error = validate_timestamp(ts)
            self.assertFalse(is_valid, f"Timestamp {ts} should be invalid")
            self.assertNotEqual(error, "")

    def test_timestamp_wrong_type(self):
        """Test timestamp with wrong data type"""
        is_valid, error = validate_timestamp(12345)
        self.assertFalse(is_valid)
        self.assertIn("must be a string", error)


class TestValidateSensors(unittest.TestCase):
    """Test cases for sensor data validation"""

    def setUp(self):
        """Set up a valid base sensor data dictionary for use across tests."""
        self.valid_sensor_data = {
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
        }

    def test_valid_sensor_data(self):
        """Test valid sensor data"""
        is_valid, errors = validate_sensors(self.valid_sensor_data)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_missing_sensor_data(self):
        """Test missing sensor data"""
        is_valid, errors = validate_sensors(None)
        self.assertFalse(is_valid)
        self.assertIn("Sensor data is missing", errors)

    def test_sensor_data_not_dict(self):
        """Test sensor data is not a dictionary"""
        is_valid, errors = validate_sensors([])
        self.assertFalse(is_valid)
        self.assertIn("must be a dictionary", errors[0])

    def test_invalid_sensor_value_type(self):
        """Test sensor with non-numeric value"""
        sensor_data = {**self.valid_sensor_data, "engine_rpm": "not-a-number"}
        is_valid, errors = validate_sensors(sensor_data)
        self.assertFalse(is_valid)
        self.assertTrue(any("must be a number" in e for e in errors))

    def test_rpm_out_of_range(self):
        """Test RPM value out of acceptable range"""
        sensor_data = {**self.valid_sensor_data, "engine_rpm": 25000}
        is_valid, errors = validate_sensors(sensor_data)
        self.assertFalse(is_valid)
        self.assertTrue(any("out of range" in e for e in errors))


class TestValidateMetadata(unittest.TestCase):
    """Test cases for metadata validation"""

    def setUp(self):
        """Set up a valid base metadata dictionary for use across tests."""
        self.valid_metadata = {
            "packet_id": "pkt_1707058503789",
            "sample_rate_hz": 100,
            "daq_version": "v2.1.3"
        }

    def test_valid_metadata(self):
        """Test valid metadata"""
        is_valid, errors = validate_metadata(self.valid_metadata)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_missing_metadata(self):
        """Test missing metadata"""
        is_valid, errors = validate_metadata(None)
        self.assertFalse(is_valid)
        self.assertIn("metadata is missing", errors[0].lower())

    def test_metadata_not_dict(self):
        """Test metadata is not a dictionary"""
        is_valid, errors = validate_metadata("not-a-dict")
        self.assertFalse(is_valid)
        self.assertIn("must be a dictionary", errors[0])

    def test_missing_required_fields(self):
        """Test metadata missing required fields"""
        is_valid, errors = validate_metadata({})
        self.assertFalse(is_valid)
        self.assertTrue(any("packet_id" in e for e in errors))

    def test_invalid_sample_rate(self):
        """Test invalid sample rate"""
        metadata = {**self.valid_metadata, "sample_rate_hz": -50}
        is_valid, errors = validate_metadata(metadata)
        self.assertFalse(is_valid)
        self.assertTrue(any("must be positive" in e for e in errors))


class TestValidatePayload(unittest.TestCase):
    """Test cases for complete payload validation"""

    def setUp(self):
        """Set up a valid base payload dictionary for use across tests."""
        self.valid_payload = {
            "timestamp": "2024-01-15T10:30:00Z",
            "session_id": "test_session_001",
            "vehicle_id": "FSAE_LSU_2024_001",
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

    def test_valid_payload_dict(self):
        """Test valid payload as dictionary"""
        is_valid, errors = validate_payload(self.valid_payload)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
if __name__ == '__main__':
    unittest.main(verbosity=2)