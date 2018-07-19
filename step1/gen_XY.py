"""
Generate X and Y for traing CNN for all edges
Please put random_walk_results dir in the same dir

X format:
	x axis is the time interval, e.g., 2016/11/01 00:00:00-00:14:59 is a 15 minute interval
	y axis is the edge_id (with direction)
	M_ij is the average speed when traveling through the edge i during the time interval j

Y format:
	1 x n vector

Usage:
	python gen_matrix.py x_rn x_cn y_len time_itv q_rate rw_wn rw_sn pgr_uri edge_table data_uri data_table
	
	param 		| meaning 								| datatype	| default val
	--------------------------------------------------------------------------------
	x_rn		| # of rows for X, must be an odd num 	| int 		| 11
	x_cn		| # of columns for X 					| int 		| 4
	y_len 		| # of element in Y 					| int 		| 2
	time_itv	| # of minutes in a time interval 		| int 		| 15
	q_rate		| minimum quality rate. If percentage 	| float 	| 0.8
			    | of valid elements in X or Y < q_rate, |			|
			    | that (X, Y) pair is dropped 			|			|
	rw_wn		| walk number for random walk, used to 	| int 		| 100
				| locate result file 					| 			|
	rw_sn 		| step number for random walk, used to  | int 		| 10
				| locate result file 					| 			|
	pgr_uri		| how to log in pgrouting database 		| string 	| "host=localhost port=5432 dbname=routing user=tom password=myPassword"
	edge_table 	| name of the table storing edge data 	| string 	| "ways"
	data_uri 	| how to log in didi data database 		| string 	| "?"
	data_table  | name of the table storing didi data 	| string 	| "?"

	We do expect data_table has the following columns:
		gid: pgrouting edge_id
		osm_id: osm edge_id
		source: pgrouting source_id
		target: pgrouting target_id
		source_osm: osm source_id
		target_osm: osm target_id
		timestamp: unix timestamp of start time
		speed: avg speed to travel through the egde in m/s

Results:
	Stored in dir "/gen_matrix_results_[gen_XY_params]"
	For each edge is stored in 
		"/gen_matrix_results/[osm_id]_[source_osm]_[target_osm].p"		
"""


import psycopg2
import os, errno, sys
import pickle

def get_column_ids(osm_id, s_osm, t_osm, rw_params):

	col_ids = [[osm_id, s_osm, t_osm]]
	walk_num, step_num = rw_params
	rw_res_fname = "random_walk_results_{walk_num}_{step_num}/{osm_id}_{s_osm}_{t_osm}.p".format( \
		osm_id = osm_id, s_osm = s_osm, t_osm = t_osm, walk_num = walk_num, step_num = step_num)

	f_res = b_res = []
	try:
		f = open(rw_res_fname)
	except IOError:
		print 'Cannot open random walk result file: {}!!!'.format(rw_res_fname)
		return []
	else:
		with f:
			f_res, b_res = pickle.load(f)

	# check if we get enough rows
	if len(f_res) + len(b_res) + 1 < x_rn:
		print 'Random walk result file: {} does not have enough neighbor edges!!!'.format(rw_res_fname)
		return []

	for i, (_, osm_id, _, _, s_osm, t_osm, _) in enumerate(f_res):
		if i > max((x_cn - 3)/2, x_cn - len(b_res) - 2):
			break
		col_ids.append([osm_id, s_osm, t_osm])

	col_ids = list(reversed(col_ids))


	for i, (_, osm_id, _, _, s_osm, t_osm, _) in enumerate(b_res):
		if i > max((x_cn - 3)/2, x_cn - len(f_res) - 2):
			break
		col_ids.append([osm_id, s_osm, t_osm])

	return col_ids


def gen_XY_for_one(dirname, gid, gen_XY_params, rw_params, db_params):
	x_rn, x_cn, y_len, time_itv, q_rate = gen_XY_params
	rw_wn, rw_sn = rw_params
	pgr_conn, edge_table_name, data_conn, data_table_name = db_params

	pgr_cur = pgr_conn.cursor()
	data_cur = data_conn.cursor()
	
	stmt = "SELECT osm_id, source_osm, target_osm FROM {table_name} WHERE gid = {gid}".format(table_name = edge_table_name, gid = gid)
	pgr_cur.execute(stmt)
	osm_id, s_osm, t_osm = pgr_cur.fetchone()

	fname = "{dirname}/{osm_id}_{s_osm}_{t_osm}.p".format( \
		dirname = dirname, osm_id = osm_id, s_osm = s_osm, t_osm = t_osm)
	if os.path.isfile(fname):
		return

	Xs = []
	Ys = []

	# read in edge_ids from random walk results
	# if random walk result does not have enough rows, 
	col_ids = get_column_ids(osm_id, s_osm, t_osm, rw_params)
	if not col_ids:
		return
	
	beginning = 1477929600 # 2016/11/01 00:00:00

	for i in range(60*24*30/time_itv - x_cn - y_len + 1):
		start_t = beginning + i * 60 * time_itv

		
		X = []
		Y = []
		X_missing_element_num = 0
		Y_missing_element_num = 0

		# build Y
		for j in range(y_len):
			ele_start_t = start_t + (x_cn + k) * 60 * time_itv
			ele_end_t = ele_start_t + 60 * time_itv

			stmt = "AVG(speed) FROM {d_table_name} WHERE osm_id = {osm_id} AND source_osm = {s_osm} AND target_osm = {t_osm} \
				AND timestamp >= {col_start_t} AND timestamp < {col_end_t}".format( \
				d_table_name = data_table_name, osm_id = osm_id, s_osm = s_osm, t_osm = t_osm, \
				col_start_t = ele_start_t, col_end_t = ele_end_t)
			data_cur.execute(stmt)
			avg_speed = data_cur.fetchone()[0]

			if avg_speed is None:
				Y_missing_element_num += 1

			Y.append(avg_speed)

		if Y_missing_element_num >= y_len * (1 - q_rate):
			print "Not enough element for Y of edge {}-{}-{} starting at {}".format(osm_id, s_osm, t_osm, start_t)
			break

		ori_osm_id, ori_s_osm, ori_t_osm = osm_id, s_osm, t_osm

		# build X
		for osm_id, s_osm, t_osm in col_ids:
			row = []
			for k in range(x_cn):
				col_start_t = start_t + k * 60 * time_itv
				col_end_t = col_start_t + 60 * time_itv

				stmt = "AVG(speed) FROM {d_table_name} WHERE osm_id = {osm_id} AND source_osm = {s_osm} AND target_osm = {t_osm} \
					AND timestamp >= {col_start_t} AND timestamp < {col_end_t}".format( \
					d_table_name = data_table_name, osm_id = osm_id, s_osm = s_osm, t_osm = t_osm, \
					col_start_t = col_start_t, col_end_t = col_end_t)
				data_cur.execute(stmt)
				avg_speed = data_cur.fetchone()[0]

				if avg_speed is None:
					X_missing_element_num += 1

				row.append(avg_speed)

			X.append(row)


		if X_missing_element_num >= x_rn * x_cn * (1 - q_rate):
			print "Not enough element for X of edge {}-{}-{} starting at {}".format(ori_osm_id, ori_s_osm, ori_t_osm, start_t)
			break

		Xs.append(X)
		Ys.append(Y)

	with open(fname, 'w') as f:
	    pickle.dump([forward_res, backward_res], f)
			


def gen_XY_for_all(argv):
	# process input argv
	argv += [None] * 11
	x_rn 		= 11 	if argv[0] is None else int(argv[0])
	x_cn 		= 4 	if argv[1] is None else int(argv[1])
	y_len 		= 2 	if argv[2] is None else int(argv[2])
	time_itv 	= 15 	if argv[3] is None else int(argv[3])
	q_rate 		= 0.8 	if argv[4] is None else float(argv[4])
	rw_wn 		= 100 	if argv[5] is None else int(argv[5])
	rw_sn 		= 10 	if argv[6] is None else int(argv[6])
	pgr_uri 	= "host=localhost port=5432 dbname=routing user=tom password=myPassword" \
						if argv[7] is None else argv[7]
	edge_table 	= "ways" \
						if argv[8] is None else argv[8]
	data_uri 	= "host=localhost port=5432 dbname=routing user=tom password=myPassword" \
						if argv[9] is None else argv[9]
	data_table 	= "ways" \
						if argv[10] is None else argv[10]

	assert x_rn%2 == 1, "x_rn must be an odd num, get wrong input: {}".format(x_rn)
	gen_XY_params = (x_rn, x_cn, y_len, time_itv, q_rate)
	rw_params = (rw_wn, rw_sn)

	# create directory to store results
	dirname = "gen_XY_results_{x_rn}_{x_cn}_{y_len}_{time_itv}_{q_rate}".format(\
		x_rn = x_rn, x_cn = x_cn, y_len = y_len, time_itv = time_itv, q_rate = q_rate)
	try:
		os.makedirs(dirname)
	except OSError as e:
		if e.errno != errno.EEXIST:
			print("something wrong when creating dir!")
			raise
	print "results are stored in dir: {dirname}".format(dirname = dirname)

	# fetch all edge ids from psql
	pgr_conn = psycopg2.connect(pgr_uri)
	data_conn = psycopg2.connect(data_uri)
	db_params = (pgr_conn, edge_table, data_conn, data_table)

	stmt = "SELECT gid FROM {table_name}".format(table_name = edge_table)
	pgr_cur = pgr_conn.cursor()
	pgr_cur.execute(stmt)

	for i, gid in enumerate(pgr_cur):
		if i%10 == 0 and i > 0:
			print "processed {} egdes".format(i)
		# Without reason, gid is in the format "(gid,)", so I use gid[0] below
		gen_XY_for_one(dirname, gid[0], gen_XY_params, rw_params, db_params)

	conn.close()


if __name__ == '__main__':
	gen_XY_for_all(sys.argv[1:])