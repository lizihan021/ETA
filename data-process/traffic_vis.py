"""
Create json file for showing traffic condition at a specific timestamp
(with most data points) on the front end

Usage: python traffic_vis.py
"""

import pickle
import json
import psycopg2
import os, errno, sys

NUM_EDGE_TO_SHOW = 21
URI = "host=localhost port=5432 dbname=routing user=tom password=myPassword"
TABLE_NAME = "ways"

def select_timestamp(conn):
	cur = conn.cursor()
	stmt = "SELECT  t.table_name AS stmt \
			FROM information_schema.tables t \
			WHERE t.table_schema = 'public' \
			AND t.table_name LIKE 'time%' ORDER BY t.table_name;"
	cur.execute(stmt)
	rows = cur.fetchall()
	tablenames = []
	for row in rows:
		tablenames.append(row[0])
	# print(len(tablenames))
	max_row = 0
	max_tablename = ""
	for name in tablenames:
		stmt = "SELECT count(*) FROM {table_name};".format(table_name = name)
		cur.execute(stmt)
		row = cur.fetchone()
		if (row[0] > max_row):
			max_row = row[0]
			max_tablename = name
	# print(max_row)
	# print(max_tablename)
	return max_tablename


def traffic_convert(dirname, conn):
	cur = conn.cursor()
	stmt = "SELECT * FROM {table_name}".format(table_name = select_timestamp(conn))
	cur.execute(stmt)
	rows = cur.fetchall()
	for row in rows:
		osm_id = row[0]
		source_osm = row[1]
		target_osm = row[2]
		predicted_speed = row[3]
		if (osm_id == -1):
			break
		# print osm_id, source_osm, target_osm, predicted_speed

		res = {}
		res["id"] = "route"
		res["type"] = "line"

		res["source"] = source = {}
		source["type"] = "geojson"
		source["data"] = data = {}

		data["type"] = "Feature"
		data["properties"] = {}
		data["geometry"] = geometry = {}

		geometry["type"] = "LineString"
		geometry["coordinates"] = get_coord(osm_id, source_osm, target_osm, conn)

		res["layout"] = layout = {}

		layout["line-join"] = "round"
		layout["line-cap"] = "round"

		res["paint"] = paint = {}

		paint["line-color"] = get_color(predicted_speed)
		paint["line-width"] = 3

		fname = dirname + "/{}_{}_{}.json".format(osm_id, source_osm, target_osm)
		with open(fname, 'w') as fp:
			json.dump(res, fp, indent = 4)


def get_coord(osm_id, source_osm, target_osm, conn):
	cur = conn.cursor()
	stmt = "SELECT ST_AsText(the_geom) FROM {table_name} \
		WHERE osm_id = {osm_id} AND source_osm = {source_osm} AND target_osm = {target_osm}".format( \
		table_name = TABLE_NAME, osm_id = osm_id, source_osm = source_osm, target_osm = target_osm)
	cur.execute(stmt)
	raw = cur.fetchone()
	if raw is None:
		stmt = "SELECT ST_AsText(the_geom) FROM {table_name} \
			WHERE osm_id = {osm_id} AND source_osm = {source_osm} AND target_osm = {target_osm}".format( \
			table_name = TABLE_NAME, osm_id = osm_id, source_osm = target_osm, target_osm = source_osm)
		cur.execute(stmt)
		raw = cur.fetchone()[0]
	else:
		raw = raw[0]

	# raw is like "LINESTRING(104.0722196 30.7256417,104.072236 30.7251308,104.0720377 30.7239533)"
	gps_strs = raw.split(")")[0].split("(")[1]

	coord = []
	for gps_str in gps_strs.split(","):
		lon_str, lat_str = gps_str.split(" ")
		coord.append([float(lon_str), float(lat_str)])
	return coord

def get_color(predicted_speed):
	if predicted_speed > 11:
		return "#00FF00"
	if predicted_speed > 10:
		return "#32FF00"
	if predicted_speed > 9:
		return "#65FF00"
	if predicted_speed > 8:
		return "#99FF00"
	if predicted_speed > 7:
		return "#CCFF00"
	if predicted_speed > 6:
		return "#FFFF00"
	if predicted_speed > 5:
		return "#FFCC00"
	if predicted_speed > 4:
		return "#FF9900"
	if predicted_speed > 3:
		return "#FF6600"
	if predicted_speed > 2:
		return "#FF3200"
	if predicted_speed > 1:
		return "#FF0000"
	return "#FF0000"

def path_convert(path_name, conn):

	osm_id, source_osm, target_osm = get_edge_from_path(path_name)

	dirname = "random_walk_front_end/{}_{}_{}".format(osm_id, source_osm, target_osm)
	try:
		os.makedirs(dirname)
	except OSError as e:
		if e.errno != errno.EEXIST:
			print "something wrong when creating dir: {}!".format(dirname)
			raise

	edges = get_edges(path_name)

	for edge in edges:
		osm_id, source_osm, target_osm, visited_num = edge
		# print osm_id, source_osm, target_osm, visited_num

		res = {}
		res["id"] = "route"
		res["type"] = "line"

		res["source"] = source = {}
		source["type"] = "geojson"
		source["data"] = data = {}

		data["type"] = "Feature"
		data["properties"] = {}
		data["geometry"] = geometry = {}

		geometry["type"] = "LineString"
		geometry["coordinates"] = get_coord(osm_id, source_osm, target_osm, conn)

		res["layout"] = layout = {}

		layout["line-join"] = "round"
		layout["line-cap"] = "round"

		res["paint"] = paint = {}

		paint["line-color"] = get_color(visited_num)
		paint["line-width"] = 8

		fname = dirname + "/{}_{}_{}.json".format(osm_id, source_osm, target_osm)
		with open(fname, 'w') as fp:
			json.dump(res, fp, indent = 4)


if __name__ == "__main__":
	# print len(sys.argv)

	conn = psycopg2.connect(URI)

	dirname = "frontend-heatmap"
	try:
		os.makedirs(dirname)
	except OSError as e:
		if e.errno != errno.EEXIST:
			print("something wrong when creating dir!")
			raise
	print "results are stored in dir: {dirname}".format(dirname = dirname)

	traffic_convert(dirname, conn)


