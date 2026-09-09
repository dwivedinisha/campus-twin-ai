CREATE TABLE IF NOT EXISTS building (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS room (
    id SERIAL PRIMARY KEY,
    building_id INTEGER NOT NULL REFERENCES building(id),
    name VARCHAR(20) UNIQUE NOT NULL,
    capacity INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS sensor_reading (
    id BIGSERIAL PRIMARY KEY,
    room_id INTEGER NOT NULL REFERENCES room(id),
    timestamp TIMESTAMP NOT NULL,
    occupancy INTEGER NOT NULL,
    temperature_c NUMERIC(4,1) NOT NULL,
    humidity_pct NUMERIC(4,1) NOT NULL,
    ac_status VARCHAR(5) NOT NULL,
    lighting_status VARCHAR(5) NOT NULL,
    class_scheduled BOOLEAN NOT NULL,
    power_kw NUMERIC(6,2) NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_anomaly BOOLEAN NOT NULL,
    anomaly_type VARCHAR(30),
    data_source VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS recommendation (
    id SERIAL PRIMARY KEY,
    room_id INTEGER NOT NULL REFERENCES room(id),
    type VARCHAR(50) NOT NULL,
    reason TEXT NOT NULL,
    proposed_action VARCHAR(100) NOT NULL,
    estimated_impact_kw NUMERIC(6,2),
    confidence NUMERIC(4,2),
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    agent_source VARCHAR(30) DEFAULT 'RULE_ENGINE',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS action_log (
    id SERIAL PRIMARY KEY,
    recommendation_id INTEGER REFERENCES recommendation(id),
    room_id INTEGER NOT NULL REFERENCES room(id),
    action VARCHAR(100) NOT NULL,
    previous_state JSONB,
    new_state JSONB,
    executed_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reading_room_time ON sensor_reading(room_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_reading_timestamp ON sensor_reading(timestamp);