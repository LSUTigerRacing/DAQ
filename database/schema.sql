CREATE TABLE IF NOT EXISTS sample_registry (
    sensor_name TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    data_type TEXT NOT NULL CHECK (data_type IN ('integer', 'float', 'boolean')),
    min_range NUMERIC,
    max_range NUMERIC,
    CONSTRAINT range_check CHECK (min_range IS NULL OR max_range IS NULL OR max_range > min_range)
);

CREATE TABLE IF NOT EXISTS daq_config (
    session_id TEXT PRIMARY KEY,
    vehicle_id TEXT NOT NULL,
    sample_rate_hz INTEGER NOT NULL CHECK (sample_rate_hz > 0),
    daq_version TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS telemetry_packets (
    timestamp TIMESTAMPTZ NOT NULL, 
    session_id TEXT NOT NULL,
    packet_id TEXT NOT NULL,
    PRIMARY KEY (timestamp, session_id, packet_id),
    CONSTRAINT fk_session FOREIGN KEY (session_id) REFERENCES daq_config (session_id)
);

CREATE TABLE IF NOT EXISTS sensor_readings (
    timestamp TIMESTAMPTZ NOT NULL,
    packet_id TEXT NOT NULL,
    sensor_name TEXT NOT NULL,
    reading_value FLOAT, 
    

    CONSTRAINT fk_sensor_registry FOREIGN KEY (sensor_name) REFERENCES sample_registry (sensor_name)
);

SELECT create_hypertable('telemetry_packets', 'timestamp', if_not_exists => TRUE);
SELECT create_hypertable('sensor_readings', 'timestamp', if_not_exists => TRUE);

CREATE INDEX idx_packets_session ON telemetry_packets(session_id, timestamp DESC);
CREATE INDEX idx_readings_sensor_time ON sensor_readings(sensor_name, timestamp DESC);