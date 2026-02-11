from validator import validate_payload
from datetime import datetime

# Generate current timestamp in ISO 8601 format
current_timestamp = datetime.utcnow().isoformat() + "Z"

json_data = {
    "timestamp": current_timestamp,  # real current time
    "sensors": [
        {
            "sensor_id": "temp_01",
            "type": "temperature",
            "value": 22.5,
            "unit": "celsius" 
        }
    ],
    "metadata": {
        "device_id": "device_001",  # unique device identifier 
        "location": {  # device location
            "latitude": 30.4515,
            "longitude": -91.1871 
        }
    }   
}

# call the function 
is_valid, errors = validate_payload(json_data)

if is_valid:
    print("Payload is valid!")
else:
    print("Validation failed:")
    for error in errors:
        print(f"  - {error}")