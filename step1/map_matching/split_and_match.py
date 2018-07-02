#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# this file is used to split GPS data by order and match the trajectory to the map
#
# usage: python split_and_match.py GPS_data_filename No_of_orders PSQL_URI ROAD_TABLE_NAME
# example: python split_and_match.py gps_20161106 100 "host=localhost port=5432 dbname=routing user=tom password=myPassword" ways
#
# In this example, the first "100" orders in "gps_20161106" will be splited. 
# The results will be stored under dir "gps_20161106_match_results", and each 
# file is an order.
#
# If No_of_orders = -1, all orders in the GPS file will be processed
#
# In each file, the data are stored as
# gps_long | gps_lat | timestamp | matched_gps_long | matched_gps_lat | edge_ID | location | distance
#

import os, errno, sys, psycopg2
from examples.map_matcher import map_match

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
	dirname = str(gps_filename) + "_match_results"
	try:
		os.makedirs(dirname)
	except OSError as e:
		if e.errno != errno.EEXIST:
			print("something wrong when creating dir!")
			raise

	print("results are stored in dir: " +  dirname)

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
			timestamp = tmp[2]
			gps = [float(tmp[3]) - longitude_bias, float(tmp[4]) - latitude_bias]

			if order_ID != prev_order_ID:

				if prev_order_ID != "":
					candidates = map_match(conn, road_table_name, gps_sequence, search_radius, max_route_distance)

					for gps, timestamp, candidate in zip(gps_sequence, timestamp_sequence, candidates):
						res_str +=   "{:.5f} ".format(gps[0]) \
								   + "{:.5f} ".format(gps[1]) \
								   + timestamp + " " \
								   + "{0:.6f} {1:.6f} ".format(*map(float, (candidate.lon, candidate.lat))) \
								   + "{0} ".format(candidate.edge.id) \
								   + "{0:.2f} ".format(candidate.location) \
								   + "{0:.2f}\n".format(candidate.distance)
								   
					f_w = open(filename, 'w')
					f_w.write(res_str)
					f_w.close()

				filename = dirname + "/" + order_ID + ".json"
				prev_order_ID = order_ID

				gps_sequence = []
				timestamp_sequence = []
				res_str = ""
				count += 1

			if count > max_order_num and max_order_num != -1:
				break

			timestamp_sequence.append(timestamp)
			gps_sequence.append(gps)

	conn.close()

if __name__ == '__main__':
	sys.exit(main(sys.argv[1:]))
