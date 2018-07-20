"""
Create json file for showing random walk result on the front end

Usage: python show_rw_res.py path_to_random_walk_result_file (support wildcard)

Params:
	Modify NUM_EDGE_TO_SHOW to change the number of edges to show
	Modify URI and TABLE_NAME so that the script can get geometry info of the edges

Results:
	Results will be stored in dir:
		random_walk_front_end/
			[osm_id]_[source_osm]_[target_osm]/
				[osm_id]_[source_osm]_[target_osm].json
"""



import pickle
import json
import psycopg2
import os, errno, sys

NUM_EDGE_TO_SHOW = 21
URI = "host=localhost port=5432 dbname=step1 user=tom password=myPassword"
TABLE_NAME = "ways"

def get_edge_from_path(path_name):
	# xxx/osm_source_target.p -> ["osm", "source", "target"]
	osm_source_target = path_name.split("/")[-1].split(".")[0].split("_")
	osm_id, source_osm, target_osm = int(osm_source_target[0]), int(osm_source_target[1]), int(osm_source_target[2])
	return osm_id, source_osm, target_osm


def get_edges(path_name):
	try:
		f = open(path_name)
	except IOError:
		print "Cannot open random walk result file: {}!!!".format(path_name)
		return []
	else:
		with f:
			f_res, b_res = pickle.load(f)

	osm_id, source_osm, target_osm = get_edge_from_path(path_name)

	edges = [[osm_id, source_osm, target_osm, 50]]

	for i, edge in enumerate(f_res):
		if i == (NUM_EDGE_TO_SHOW - 1)/2:
			break
		edges.append(edge)
	for i, edge in enumerate(b_res):
		if i == (NUM_EDGE_TO_SHOW - 1)/2:
			break
		edges.append(edge)

	return edges

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

def get_color(visited_num):
	if visited_num >= 50:
		return "#FF0000"
	if visited_num >= 40:
		return "#FFAA00"
	if visited_num >= 30:
		return "#FFFF00"
	if visited_num >= 20:
		return "#00FF00"
	if visited_num >= 10:
		return "#00FFFF"
	return "#0000FF"

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
	if len(sys.argv) < 2:
		print("usage: python show_rw_res.py *.p")
		sys.exit()

	num_files = len(sys.argv) - 1
	print "number of files to convert:", num_files

	conn = psycopg2.connect(URI)

	dirname = "random_walk_front_end"
	try:
		os.makedirs(dirname)
	except OSError as e:
		if e.errno != errno.EEXIST:
			print("something wrong when creating dir!")
			raise
	print "results are stored in dir: {dirname}".format(dirname = dirname)

	for path_name in sys.argv[1:]:
		path_convert(path_name, conn)