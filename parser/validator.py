"""
JSON Payload Validator Module

This module provides validation functions for JSON payloads in the data pipeline.
It validates payload structure, sensor data, and metadata fields.
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
    Validate sensor readings data.
    
    Args:
        sensor_data: Sensor data to validate (expected to be a list of sensor readings)
        
    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    errors = []
    
    # Check if sensor_data exists
    if sensor_data is None:
        errors.append("Sensor data is missing")
        return False, errors
    
    # Check if sensor_data is a list
    if not isinstance(sensor_data, list):
        errors.append(f"Sensor data must be a list, got {type(sensor_data).__name__}")
        return False, errors
    
    # Check if list is not empty
    if len(sensor_data) == 0:
        errors.append("Sensor data list cannot be empty")
        return False, errors
    
    # Validate each sensor reading
    for idx, sensor in enumerate(sensor_data):
        if not isinstance(sensor, dict):
            errors.append(f"Sensor at index {idx} must be a dictionary, got {type(sensor).__name__}")
            continue
        
        # Required fields for each sensor
        required_fields = ['sensor_id', 'type', 'value', 'unit']
        for field in required_fields:
            if field not in sensor:
                errors.append(f"Sensor at index {idx} missing required field: '{field}'")
        
        # Validate sensor_id
        if 'sensor_id' in sensor:
            if not isinstance(sensor['sensor_id'], str):
                errors.append(f"Sensor at index {idx}: sensor_id must be a string")
            elif not sensor['sensor_id'].strip():
                errors.append(f"Sensor at index {idx}: sensor_id cannot be empty")
        
        # Validate type
        if 'type' in sensor:
            if not isinstance(sensor['type'], str):
                errors.append(f"Sensor at index {idx}: type must be a string")
            else:
                valid_types = ['temperature', 'humidity', 'pressure', 'light', 'motion', 'proximity', 'accelerometer', 'gyroscope']
                if sensor['type'].lower() not in valid_types:
                    errors.append(f"Sensor at index {idx}: type '{sensor['type']}' is not a recognized sensor type")
        
        # Validate value
        if 'value' in sensor:
            if not isinstance(sensor['value'], (int, float)):
                errors.append(f"Sensor at index {idx}: value must be a number (int or float)")
            else:
                # Range validation based on sensor type
                sensor_type = sensor.get('type', '').lower()
                value = sensor['value']
                
                if sensor_type == 'temperature':
                    if value < -273.15 or value > 1000:  # Celsius, absolute zero to reasonable max
                        errors.append(f"Sensor at index {idx}: temperature value {value} is out of acceptable range (-273.15 to 1000)")
                elif sensor_type == 'humidity':
                    if value < 0 or value > 100:
                        errors.append(f"Sensor at index {idx}: humidity value {value} is out of acceptable range (0 to 100)")
                elif sensor_type == 'pressure':
                    if value < 0 or value > 2000:  # hPa or mbar
                        errors.append(f"Sensor at index {idx}: pressure value {value} is out of acceptable range (0 to 2000)")
                elif sensor_type == 'light':
                    if value < 0:
                        errors.append(f"Sensor at index {idx}: light value {value} cannot be negative")
        
        # Validate unit
        if 'unit' in sensor:
            if not isinstance(sensor['unit'], str):
                errors.append(f"Sensor at index {idx}: unit must be a string")
        
        # Validate timestamp if present
        if 'timestamp' in sensor:
            is_valid, error_msg = validate_timestamp(sensor['timestamp'])
            if not is_valid:
                errors.append(f"Sensor at index {idx}: {error_msg}")
    
    return len(errors) == 0, errors


def validate_metadata(metadata: Any) -> Tuple[bool, List[str]]:
    """
    Validate metadata fields.
    
    Args:
        metadata: Metadata dictionary to validate
        
    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    errors = []
    
    # Check if metadata exists
    if metadata is None:
        errors.append("Metadata is missing")
        return False, errors
    
    # Check if metadata is a dictionary
    if not isinstance(metadata, dict):
        errors.append(f"Metadata must be a dictionary, got {type(metadata).__name__}")
        return False, errors
    
    # Required metadata fields
    required_fields = ['device_id', 'location']
    for field in required_fields:
        if field not in metadata:
            errors.append(f"Metadata missing required field: '{field}'")
    
    # Validate device_id
    if 'device_id' in metadata:
        if not isinstance(metadata['device_id'], str):
            errors.append("Metadata: device_id must be a string")
        elif not metadata['device_id'].strip():
            errors.append("Metadata: device_id cannot be empty")
    
    # Validate location
    if 'location' in metadata:
        if not isinstance(metadata['location'], dict):
            errors.append(f"Metadata: location must be a dictionary, got {type(metadata['location']).__name__}")
        else:
            location = metadata['location']
            
            # Check for required location fields
            if 'latitude' not in location:
                errors.append("Metadata: location missing 'latitude'")
            elif not isinstance(location['latitude'], (int, float)):
                errors.append("Metadata: location.latitude must be a number")
            elif location['latitude'] < -90 or location['latitude'] > 90:
                errors.append(f"Metadata: location.latitude {location['latitude']} is out of range (-90 to 90)")
            
            if 'longitude' not in location:
                errors.append("Metadata: location missing 'longitude'")
            elif not isinstance(location['longitude'], (int, float)):
                errors.append("Metadata: location.longitude must be a number")
            elif location['longitude'] < -180 or location['longitude'] > 180:
                errors.append(f"Metadata: location.longitude {location['longitude']} is out of range (-180 to 180)")
    
    # Validate firmware_version if present
    if 'firmware_version' in metadata:
        if not isinstance(metadata['firmware_version'], str):
            errors.append("Metadata: firmware_version must be a string")
    
    # Validate battery_level if present
    if 'battery_level' in metadata:
        if not isinstance(metadata['battery_level'], (int, float)):
            errors.append("Metadata: battery_level must be a number")
        elif metadata['battery_level'] < 0 or metadata['battery_level'] > 100:
            errors.append(f"Metadata: battery_level {metadata['battery_level']} is out of range (0 to 100)")
    
    return len(errors) == 0, errors


def validate_payload(json_data: Any) -> Tuple[bool, List[str]]:
    """
    Validate complete payload structure.
    
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
    required_fields = ['timestamp', 'sensors', 'metadata']
    for field in required_fields:
        if field not in data:
            errors.append(f"Payload missing required field: '{field}'")
    
    # Validate timestamp
    if 'timestamp' in data:
        is_valid, error_msg = validate_timestamp(data['timestamp'])
        if not is_valid:
            errors.append(f"Payload: {error_msg}")
    
    # Validate sensors
    if 'sensors' in data:
        is_valid, sensor_errors = validate_sensors(data['sensors'])
        errors.extend(sensor_errors)
    
    # Validate metadata
    if 'metadata' in data:
        is_valid, metadata_errors = validate_metadata(data['metadata'])
        errors.extend(metadata_errors)
    
    return len(errors) == 0, errors


def validate_payload_strict(json_data: Any) -> Dict[str, Any]:
    """
    Validate payload and raise ValidationError if invalid.
    
    Args:
        json_data: JSON payload to validate
        
    Returns:
        Dictionary containing validation results
        
    Raises:
        ValidationError: If validation fails
    """
    is_valid, errors = validate_payload(json_data)
    
    if not is_valid:
        error_message = "Validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
        raise ValidationError(error_message)
    
    return {
        "valid": True,
        "errors": [],
        "message": "Payload validation successful"
    }