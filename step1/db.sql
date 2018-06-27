CREATE DATABASE mapdb;
CREATE TABLE map(
	gps_long	DOUBLE PRECISION,
	gps_lat		DOUBLE PRECISION,
	timestamp	BIGINT,
	matched_gps_long	DOUBLE PRECISION,
	matched_gps_lat		DOUBLE PRECISION,
	edge_ID		INTEGER,
	location	REAL,
	distance	REAL
);
\copy map FROM 'map.json' DELIMITER ' ' CSV
