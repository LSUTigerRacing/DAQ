CREATE TABLE IF NOT EXISTS sample_registry (
sensor_name TEXT PRIMARY KEY,
description TEXT NOT NULL,
data_type TEXT NOT NULL CHECK (data_type IN ('integer', 'float', 'boolean' )),
min_range NUMERIC,
max_range NUMERIC,
CONSTRAINT range_check CHECK ( min_range IS NULL OR max_range IS NULL OR max_range > min_range),
);

create TABLE IF NOT EXISTS daq_config (
  session_id TEXT PRIMARY KEY,
  vehicle_id TEXT NOT NULL,
  sample_rate_hz INTEGER NOT NULL CHECK (sample_rate_hz > 0),
  daq_version TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS telemetry_data(
-- Date & Timezone --
time TIMESTAMPTZ NOT NULL,
session_id TEXT NOT NULL,
packet_id TEXT NOT NULL,

 -- Sensor data information --
 engine_rpm INTEGER CHECK (engine_rpm >= 0),
 throttle_position FLOAT CHECK(throttle_position BETWEEN 0 AND 100),
 brake_pressure FLOAT CHECK(brake_pressure >=0),
 coolant_temp FLOAT,
 oil_pressure FLOAT CHECK(oil_pressure >= 0),
 intake_air_temp FLOAT,
 battery_voltage FLOAT CHECK(battery_voltage BETWEEN 0 AND 18),
 speed_fl FLOAT,
 speed_fr FLOAT,
 speed_rl FLOAT,
 speed_rr FLOAT,
 steering_angle FLOAT,
 accel_lateral FLOAT,
 accel_longitudinal FLOAT,

 PRIMARY KEY (time, session_id, packet_id),
   CONSTRAINT fk_session FOREIGN KEY (session_id) REFERENCES daq_config (session_id)
);


 SELECT create_hypertable('telemetry_data', 'time', if_not_exists => TRUE);
 CREATE INDEX idx_telemetry_session_time ON telemetry_data(session_id, time DESC);
 CREATE INDEX idx_telemetry_packet ON telemetry_data (packet_id);