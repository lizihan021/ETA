"""
Conduct random walk for all edges

Usage:
	python random_walk.py walk_num step_num_in_one_walk [uri] [table_name] (uri and table_name are optional)

Example:
	python random_walk.py 100 10 "host=localhost port=5432 dbname=routing user=tom password=myPassword" ways
Meaning:
	For each edge in routing/ways, random_walk.py will conduct 100 random walks starting from that edge
	Each walk contains 10 steps (10 edges, starting edge not included)
	Half of the walks are forward along the edge, and the other half are backward

Results:
	Stored in dir "/random_walk_results_[rw_params]"
	For each edge is stored in 
		"/random_walk_results_[rw_params]/[osm_id]_[source_osm]_[target_osm].p"
	
	The rows in txt are sorted descendingly according to the "# of times being visited"
"""

import psycopg2
import os, errno, sys
import random
import pickle

def get_nodes(edge, edge_node_dict, conn, table_name):
	if edge in edge_node_dict:
		return edge_node_dict[edge]

	stmt = "SELECT source, target FROM {table_name} WHERE gid = {gid}".format(table_name = table_name, gid = edge)
	cur = conn.cursor()
	cur.execute(stmt)
	source, target = cur.fetchone()
	edge_node_dict[edge] = (source, target)
	return (source, target)

def get_edges(node, is_forward, node_edge_dict, conn, table_name):
	if (node, is_forward) in node_edge_dict:
		return node_edge_dict[(node, is_forward)]

	if is_forward:
		stmt = "SELECT gid FROM {table_name} WHERE source = {source}".format(table_name = table_name, source = node)
	else:
		stmt = "SELECT gid FROM {table_name} WHERE target = {target}".format(table_name = table_name, target = node)

	cur = conn.cursor()
	cur.execute(stmt)
	edges = []
	for gid in cur:
		edges.append(gid[0]) # Without reason, gid is in the format "(gid,)"
	node_edge_dict[(node, is_forward)] = edges
	return edges

def random_walk_for_one(dirname, gid, osm_id, walk_num, step_num, conn, table_name):
	# check if result file already exist
	cur = conn.cursor()
	stmt = "SELECT source_osm, target_osm FROM {table_name} WHERE gid = {gid}".format(table_name = table_name, gid = gid)
	cur.execute(stmt)
	source_osm, target_osm = cur.fetchone()

	fname = "{dirname}/{osm_id}_{source_osm}_{target_osm}.p".format( \
		dirname = dirname, osm_id = osm_id, source_osm = source_osm, target_osm = target_osm)
	if os.path.isfile(fname):
		return

	node_edge_dict = {}
	edge_node_dict = {}
	edge_visited_num = {}
	for i in range(walk_num):
		is_forward = 2*i >= walk_num

		edge = gid
		# edge_visited_num[(edge, is_forward)] = edge_visited_num.get((edge, is_forward), 0) + 1

		for _ in range(step_num):
			source, target = get_nodes(edge, edge_node_dict, conn, table_name)
			node = target if is_forward else source
			edges = get_edges(node, is_forward, node_edge_dict, conn, table_name)
			if not edges:
				# reach dead end
				break
			edge = random.choice(edges)
			edge_visited_num[(edge, is_forward)] = edge_visited_num.get((edge, is_forward), 0) + 1

	# sort walk result in descending order
	results = []
	for (edge, is_forward), visited_num in edge_visited_num.iteritems():
		results.append([visited_num, (edge, is_forward)])
	results.sort(reverse = True)

	forward_res = []
	backward_res = []
	
	for visited_num, (edge, is_forward) in results:
		stmt = "SELECT gid, osm_id, source, target, source_osm, target_osm FROM {table_name} WHERE gid = {gid}".format(table_name = table_name, gid = edge)
		cur.execute(stmt)
		gid, osm_id, source, target, source_osm, target_osm = cur.fetchone()
		if is_forward:
			forward_res.append([gid, osm_id, source, target, source_osm, target_osm, visited_num])
		else:
			backward_res.append([gid, osm_id, source, target, source_osm, target_osm, visited_num])

	with open(fname, 'w') as f:
	    pickle.dump([forward_res, backward_res], f)

def random_walk_for_all(argv):
	if len(argv) != 2 and len(argv) != 4:
		print("usage: python random_walk.py walk_num step_num_in_one_walk uri table_name (uri and table_name are optional)")
		sys.exit()

	walk_num, step_num = int(argv[0]), int(argv[1])
	if len(argv) == 4:
		uri, table_name = argv[2], argv[3]
	else:
		uri, table_name = "host=localhost port=5432 dbname=routing user=tom password=myPassword", "ways"

	# create directory to store results
	dirname = "random_walk_results_{walk_num}_{step_num}".format(walk_num = walk_num, step_num = step_num)
	try:
		os.makedirs(dirname)
	except OSError as e:
		if e.errno != errno.EEXIST:
			print("something wrong when creating dir!")
			raise
	print "results are stored in dir: {dirname}".format(dirname = dirname)

	# fetch all edge ids from psql
	conn = psycopg2.connect(uri)
	stmt = "SELECT gid FROM {table_name}".format(table_name = table_name)
	cur = conn.cursor()
	cur.execute(stmt)

	for i, gid in enumerate(cur):
		if i%10 == 0 and i > 0:
			print "processed {} egdes".format(i)
		# Without reason, gid is in the format "(gid,)", so I use gid[0] below
		random_walk_for_one(dirname, gid[0], osm_id, walk_num, step_num, conn, table_name)

	conn.close()

if __name__ == '__main__':
	random_walk_for_all(sys.argv[1:]);