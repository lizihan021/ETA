import psycopg2

DB_NAME = "step1"
TABLE_NAME = "edge_speed"
NEW_TABLE_NAME = "step1_ways"

if __name__ == '__main__':
	uri = "host=localhost port=5432 dbname={} user=tom password=myPassword".format(DB_NAME)
	conn = psycopg2.connect(uri)
	cur = conn.cursor()
	cur1 = conn.cursor()

	stmt = "SELECT DISTINCT gid, osm_id, source, target, source_osm, target_osm FROM {}".format(TABLE_NAME)
	cur.execute(stmt)
	for gid, osm_id, source, target, source_osm, target_osm in cur:
		stmt = "INSERT INTO {0}(gid, osm_id, source, target, source_osm, target_osm) \
			VALUES ({1}, {2}, {3}, {4}, {5}, {6})".format(NEW_TABLE_NAME, gid, osm_id, source, target, source_osm, target_osm)
		cur1.execute(stmt)
	conn.commit()