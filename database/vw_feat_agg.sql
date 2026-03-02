CREATE MATERIALIZED VIEW IF NOT EXISTS split_sensor_data_by_filter
with (timescaledb.continuous) AS

SELECT
timebucket('1 minute', timestamp) AS bucket,

sensor_name,


AVG(value) AS avg_value,
MIN(value) AS min_value,
MAX(value) AS max_value,
COUNT(*) AS reading_count

FROM sensor_readings
GROUP BY bucket, sensor_name;

