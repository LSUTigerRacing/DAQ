"""
JSON Payload Validator Module for Formula SAE Racing Telemetry

This module provides validation functions for JSON payloads containing
Formula SAE racing car telemetry data before entering the data pipeline.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Tuple


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


def validate_timestamp(timestamp_str: str) -> Tuple[bool, str]:
    """
    Validate that a timestamp is in valid ISO 8601 format.
    
    Args:
        timestamp_str: String to validate as ISO 8601 timestamp
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(timestamp_str, str):
        return False, f"Timestamp must be a string, got {type(timestamp_str).__name__}"
    
    # Check that timestamp contains time component (has 'T' separator)
    if 'T' not in timestamp_str:
        return False, f"Invalid ISO 8601 timestamp format: {timestamp_str}. Must include time component (e.g., 2024-01-15T10:30:00Z)"
    
    try:
        # Try parsing as ISO 8601 format
        datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return True, ""
    except ValueError as e:
        return False, f"Invalid ISO 8601 timestamp format: {timestamp_str}. Error: {str(e)}"


def validate_sensors(sensor_data: Any) -> Tuple[bool, List[str]]:
    """
    Validate racing sensor readings data.
    
    Args:
        sensor_data: Sensor data dictionary to validate
        
    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    errors = []
    
    # Check if sensor_data exists
    if sensor_data is None:
        errors.append("Sensor data is missing")
        return False, errors
    
    # Check if sensor_data is a dictionary
    if not isinstance(sensor_data, dict):
        errors.append(f"Sensor data must be a dictionary, got {type(sensor_data).__name__}")
        return False, errors
    
    # Define required sensor fields for FSAE telemetry
    required_fields = [
        'engine_rpm',
        'throttle_position',
        'brake_pressure',
        'coolant_temp',
        'oil_pressure',
        'intake_air_temp',
        'battery_voltage',
        'speed_fl',
        'speed_fr',
        'speed_rl',
        'speed_rr',
        'steering_angle',
        'accel_lateral',
        'accel_longitudinal'
    ]
    
    # Check for required fields
    for field in required_fields:
        if field not in sensor_data:
            errors.append(f"Sensors missing required field: '{field}'")
    
    # Define validation rules: (min_value, max_value, description)
    sensor_validations = {
        'engine_rpm': (0, 14000, "RPM must be between 0 and 14000"),
        'throttle_position': (0, 100, "Throttle position must be between 0 and 100 percent"),
        'brake_pressure': (0, 2000, "Brake pressure must be between 0 and 2000 bar/psi"),
        'coolant_temp': (20, 120, "Coolant temperature must be between 20 and 120 degrees C"),
        'oil_pressure': (0, 100, "Oil pressure must be between 0 and 100 psi"),
        'intake_air_temp': (-10, 80, "Intake air temperature must be between -10 and 80 degrees C"),
        'battery_voltage': (10, 15, "Battery voltage must be between 10 and 15 volts"),
        'speed_fl': (0, 45, "Front left wheel speed must be between 0 and 45 mph"),
        'speed_fr': (0, 45, "Front right wheel speed must be between 0 and 45 mph"),
        'speed_rl': (0, 45, "Rear left wheel speed must be between 0 and 45 mph"),
        'speed_rr': (0, 45, "Rear right wheel speed must be between 0 and 45 mph"),
        'steering_angle': (-540, 540, "Steering angle must be between -540 and 540 degrees"),
        'accel_lateral': (-3, 3, "Lateral acceleration must be between -3 and 3 g"),
        'accel_longitudinal': (-3, 3, "Longitudinal acceleration must be between -3 and 3 g")
    }
    
    # Validate each sensor field
    for field, (min_val, max_val, description) in sensor_validations.items():
        if field in sensor_data:
            value = sensor_data[field]
            
            # Check if value is numeric
            if not isinstance(value, (int, float)):
                errors.append(f"Sensors: {field} must be a number (int or float), got {type(value).__name__}")
            else:
                # Check range
                if value < min_val or value > max_val:
                    errors.append(f"Sensors: {field} value {value} is out of range. {description}")
    
    return len(errors) == 0, errors


def validate_metadata(metadata: Any) -> Tuple[bool, List[str]]:
    """
    Validate telemetry metadata fields.
    
    Args:
        metadata: Metadata dictionary to validate
        
    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    errors = []
    
    # Check if metadata exists
    if metadata is None:
        errors.append("Telemetry metadata is missing")
        return False, errors
    
    # Check if metadata is a dictionary
    if not isinstance(metadata, dict):
        errors.append(f"Telemetry metadata must be a dictionary, got {type(metadata).__name__}")
        return False, errors
    
    # Required metadata fields
    required_fields = ['packet_id', 'sample_rate_hz', 'daq_version']
    for field in required_fields:
        if field not in metadata:
            errors.append(f"Telemetry metadata missing required field: '{field}'")
    
    # Validate packet_id
    if 'packet_id' in metadata:
        if not isinstance(metadata['packet_id'], str):
            errors.append("Telemetry metadata: packet_id must be a string")
        elif not metadata['packet_id'].strip():
            errors.append("Telemetry metadata: packet_id cannot be empty")
    
    # Validate sample_rate_hz
    if 'sample_rate_hz' in metadata:
        if not isinstance(metadata['sample_rate_hz'], (int, float)):
            errors.append("Telemetry metadata: sample_rate_hz must be a number")
        elif metadata['sample_rate_hz'] <= 0:
            errors.append(f"Telemetry metadata: sample_rate_hz must be positive, got {metadata['sample_rate_hz']}")
        elif metadata['sample_rate_hz'] > 10000:
            errors.append(f"Telemetry metadata: sample_rate_hz {metadata['sample_rate_hz']} exceeds maximum (10000 Hz)")
    
    # Validate daq_version
    if 'daq_version' in metadata:
        if not isinstance(metadata['daq_version'], str):
            errors.append("Telemetry metadata: daq_version must be a string")
    
    return len(errors) == 0, errors


def validate_payload(json_data: Any) -> Tuple[bool, List[str]]:
    """
    Validate complete FSAE telemetry payload structure.
    
    Args:
        json_data: JSON payload to validate (can be dict or JSON string)
        
    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    errors = []
    
    # If json_data is a string, try to parse it
    if isinstance(json_data, str):
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON format: {str(e)}")
            return False, errors
    elif isinstance(json_data, dict):
        data = json_data
    else:
        errors.append(f"Payload must be a JSON string or dictionary, got {type(json_data).__name__}")
        return False, errors
    
    # Check for required top-level fields
    required_fields = ['timestamp', 'session_id', 'vehicle_id', 'sensors', 'telemetry_metadata']
    for field in required_fields:
        if field not in data:
            errors.append(f"Payload missing required field: '{field}'")
    
    # Validate timestamp
    if 'timestamp' in data:
        is_valid, error_msg = validate_timestamp(data['timestamp'])
        if not is_valid:
            errors.append(f"Payload: {error_msg}")
    
    # Validate session_id
    if 'session_id' in data:
        if not isinstance(data['session_id'], str):
            errors.append("Payload: session_id must be a string")
        elif not data['session_id'].strip():
            errors.append("Payload: session_id cannot be empty")
    
    # Validate vehicle_id
    if 'vehicle_id' in data:
        if not isinstance(data['vehicle_id'], str):
            errors.append("Payload: vehicle_id must be a string")
        elif not data['vehicle_id'].strip():
            errors.append("Payload: vehicle_id cannot be empty")
    
    # Validate sensors
    if 'sensors' in data:
        is_valid, sensor_errors = validate_sensors(data['sensors'])
        errors.extend(sensor_errors)
    
    # Validate telemetry_metadata
    if 'telemetry_metadata' in data:
        is_valid, metadata_errors = validate_metadata(data['telemetry_metadata'])
        errors.extend(metadata_errors)
    
    return len(errors) == 0, errors


def validate_payload_strict(json_data: Any) -> Dict[str, Any]:
    """
    Validate payload and raise ValidationError if invalid.
    
    """
    is_valid, errors = validate_payload(json_data)
    
    if not is_valid:
        error_message = "Validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
        raise ValidationError(error_message)
    
    return {
        "valid": True,
        "errors": [],
        "message": "FSAE telemetry payload validation successful"
    }