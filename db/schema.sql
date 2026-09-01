CREATE TABLE building (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE room (
    id SERIAL PRIMARY KEY,
    building_id INTEGER NOT NULL REFERENCES building(id),
    name VARCHAR(20) UNIQUE NOT NULL,
    capacity INTEGER NOT NULL
);

CREATE TABLE sensor_reading (
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

CREATE INDEX idx_reading_room_time ON sensor_reading(room_id, timestamp);
CREATE INDEX idx_reading_timestamp ON sensor_reading(timestamp);