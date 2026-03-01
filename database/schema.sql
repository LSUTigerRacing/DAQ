CREATE TABLE IF NOT EXISTS sensor_registry (
    sensor_name TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    data_type TEXT NOT NULL CHECK (data_type IN ('integer', 'float', 'boolean')),
    min_range NUMERIC,
    max_range NUMERIC,
    CONSTRAINT range_check CHECK (min_range IS NULL OR max_range IS NULL OR max_range > min_range)
);

CREATE TABLE IF NOT EXISTS packets (
    packet_id TEXT PRIMARY KEY, -- requested PK
    timestamp TIMESTAMPTZ NOT NULL, 
    session_id TEXT NOT NULL,
    vehicle_id TEXT NOT NULL,
    sample_rate_hz INTEGER NOT NULL CHECK (sample_rate_hz = 100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sensor_readings (
    timestamp TIMESTAMPTZ NOT NULL,
    packet_id TEXT NOT NULL,
    sensor_name TEXT NOT NULL,
    value FLOAT, 

    CONSTRAINT fk_packet_id FOREIGN KEY (packet_id) REFERENCES packets (packet_id),
    CONSTRAINT fk_sensor_registry FOREIGN KEY (sensor_name) REFERENCES sensor_registry (sensor_name)
);

-- TimescaleDB Hypertable Setup
SELECT create_hypertable('packets', 'timestamp', if_not_exists => TRUE);
SELECT create_hypertable('sensor_readings', 'timestamp', if_not_exists => TRUE);

-- Indexes for performance
CREATE INDEX idx_packets_session ON packets(session_id, timestamp DESC);
CREATE INDEX idx_readings_sensor_time ON sensor_readings(sensor_name, timestamp DESC);