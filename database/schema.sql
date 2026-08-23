CREATE TABLE IF NOT EXISTS sensor_readings (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    temperature DOUBLE PRECISION NOT NULL,
    vibration DOUBLE PRECISION NOT NULL,
    current DOUBLE PRECISION NOT NULL,
    status VARCHAR(30) NOT NULL,
    predicted_status VARCHAR(30),
    machine_id VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS predictive_readings (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    temperature DOUBLE PRECISION NOT NULL,
    vibration DOUBLE PRECISION NOT NULL,
    current DOUBLE PRECISION NOT NULL,
    current_status VARCHAR(30) NOT NULL,
    future_failure INTEGER NOT NULL,
    failure_probability DOUBLE PRECISION NOT NULL,
    predictive_state VARCHAR(30) NOT NULL,
    machine_id VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS ml_alerts (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    alert_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    temperature DOUBLE PRECISION,
    vibration DOUBLE PRECISION,
    current DOUBLE PRECISION,
    predicted_status VARCHAR(30),
    machine_id VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS maintenance_events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    machine_id VARCHAR(20) NOT NULL,
    event_type VARCHAR(30) NOT NULL,
    message TEXT
);

CREATE INDEX IF NOT EXISTS idx_sensor_readings_machine_time
ON sensor_readings (machine_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_predictive_readings_machine_time
ON predictive_readings (machine_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_ml_alerts_machine_time
ON ml_alerts (machine_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_maintenance_events_machine_time
ON maintenance_events (machine_id, timestamp DESC);