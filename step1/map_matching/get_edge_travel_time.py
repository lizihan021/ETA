#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# this file is used to split GPS data by order, match the trajectory to the map and calculate travel time for each edge
#
# usage: python get_edge_travel_time.py GPS_data_filename No_of_orders PSQL_URI ROAD_TABLE_NAME
# example: python split_and_match.py gps_20161106 100 "host=localhost port=5432 dbname=routing user=tom password=myPassword" ways
#
# In this example, the first "100" orders in "gps_20161106" will be splited. 
# The results will be stored under dir "gps_20161106_edge_travel_time", and 
# each file is an order.
#
# If No_of_orders = -1, all orders in the GPS file will be processed
#
# In each file, the data are stored as
# edge_id | osm_id  | start_time  | day_of_the_week | travel_time (seconds) | source | target | source_osm_id | target_osm_id 
# int     | int     | str         | int             | int                   | int    | int    | int           | int
# 1       | 5131313 | 2016-11-

import os, errno, sys, psycopg2
import datetime, pytz
from examples.map_matcher import map_match

def timestamp2time(timestamp):
	"""
	convert unix timestamp (int) to time str in Beijing timezone with format (%Y-%m-%d %H:%M:%S, weekday+)
	"""
	old_timezone = pytz.timezone("UTC")
	new_timezone = pytz.timezone("Asia/Chongqing")
	old_timestamp = datetime.datetime.utcfromtimestamp(timestamp)
	new_timestamp = old_timezone.localize(old_timestamp).astimezone(new_timezone)
	return new_timestamp.strftime('%Y-%m-%d %H:%M:%S'), new_timestamp.weekday()

def get_result_str(conn, gps_sequence, timestamp_sequence, candidates):
	"""
	will ignore the first and last edge in a trajectroy, since they are incomplete
	"""

	cur = conn.cursor()

	res_str = ""
	new_edge_id = current_edge_id = candidates[0].edge.id
	current_node1 = current_node2 = current_node1_osm_id = current_node2_osm_id = 0
	source = target = source_osm_id = target_osm_id = 0
	current_start_time = 0

	for gps, timestamp, candidate in zip(gps_sequence, timestamp_sequence, candidates):
		new_edge_id = candidate.edge.id

		if new_edge_id != current_edge_id:

			# update time
			start_time_str, start_time_weekday = timestamp2time(current_start_time)

			# update travel time
			travel_time = timestamp - current_start_time

			stmt = '''SELECT * FROM ways WHERE gid = {0}'''.format(new_edge_id)
			cur.execute(stmt)
			row = cur.fetchall()[0]
			new_edge_osm_id = row[1]
			new_node1, new_node2, new_node1_osm_id, new_node2_osm_id = row[6:10]
			print row

			is_edge_valid = True
			if current_node1 == 0:
			# not to include the first edge becuase it may be incomplete
				is_edge_valid = False
			else:
				if new_node1 == current_node1 or new_node2 == current_node1:
					source, target = current_node2, current_node1
					source_osm_id, target_osm_id = current_node2_osm_id, current_node1_osm_id
				elif new_node1 == current_node2 or new_node2 == current_node2:
					source, target = current_node1, current_node2
					source_osm_id, target_osm_id = current_node1_osm_id, current_node2_osm_id
				else:
					is_edge_valid = False

			if is_edge_valid:
				res_str +=   "{0}\t{1}\t".format(current_edge_id, current_edge_osm_id) \
						   + start_time_str + "\t" + str(start_time_weekday) + "\t" \
						   + "{0}\t".format(travel_time) \
						   + "{0}\t{1}\t".format(source, target) \
						   + "{0}\t{1}\n".format(source_osm_id, target_osm_id)

			current_edge_id, current_edge_osm_id = new_edge_id, new_edge_osm_id			
			current_start_time = timestamp
			current_node1, current_node2 = new_node1, new_node2
			current_node1_osm_id, current_node2_osm_id = new_node1_osm_id, new_node2_osm_id

	cur.close()

	return res_str


def main(argv):
	if len(argv) != 4:
		print("usage: python split_and_match.py GPS_data_filename No_of_orders PSQL_URI ROAD_TABLE_NAME")
		sys.exit()

	gps_filename = argv[0]
	max_order_num = int(argv[1]) 
	uri = argv[2]
	road_table_name = argv[3]

	# hyperparam for map matching
	search_radius = 30
	max_route_distance = 200

	# bias between Didi GPS and OpenStreetMap GPS
	longitude_bias = 0.0026
	latitude_bias = -0.0023

	count = 0

	# create directory to store all orders
	dirname = str(gps_filename) + "_edge_travel_time"
	try:
		os.makedirs(dirname)
	except OSError as e:
		if e.errno != errno.EEXIST:
			print("something wrong when creating dir!")
			raise

	print("created dir: " +  dirname)

	filename = ""
	prev_order_ID, order_ID = "", ""

	gps_sequence = []
	timestamp_sequence = []
	res_str = ""

	conn = psycopg2.connect(uri)

	with open(gps_filename, 'r') as f:
		for line in f:
			tmp = line[:-1].split(",")
			order_ID = tmp[1]
			timestamp = int(tmp[2])
			gps = [float(tmp[3]) - longitude_bias, float(tmp[4]) - latitude_bias]

			if order_ID != prev_order_ID:

				if prev_order_ID != "":
					candidates = map_match(conn, road_table_name, gps_sequence, search_radius, max_route_distance)

					res_str = get_result_str(conn, gps_sequence, timestamp_sequence, candidates)
								   
					f_w = open(filename, 'w')
					f_w.write(res_str)
					f_w.close()

				filename = dirname + "/" + order_ID + ".json"
				prev_order_ID = order_ID

				gps_sequence = []
				timestamp_sequence = []
				res_str = ""
				count += 1

			if count > max_order_num and max_order_num != 0:
				break

			timestamp_sequence.append(timestamp)
			gps_sequence.append(gps)

	conn.close()

if __name__ == '__main__':
	sys.exit(main(sys.argv[1:]))
