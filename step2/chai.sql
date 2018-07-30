CREATE TABLE edge_speed_1 (
	id SERIAL PRIMARY KEY,
    osm_id bigint NOT NULL,
    "timestamp" bigint,
    speed double precision,
    source_osm bigint NOT NULL,
    target_osm bigint NOT NULL
);

INSERT INTO edge_speed_2 (osm_id, timestamp, speed, source_osm, target_osm)
SELECT osm_id, timestamp, speed, source_osm, target_osm
FROM edge_speed WHERE id > 40000000 AND id <= 80000000;