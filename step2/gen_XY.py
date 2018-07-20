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
	python gen_matrix.py x_rn x_cn y_len time_itv q_rate rw_wn rw_sn uri table_name
	
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
	uri 		| how to log in step1_res database 		| string 	| "host=localhost port=5432 dbname=step1 user=tom password=myPassword"
	table_name 	| name of the table storing map 	 	| string 	| "edge_speed"
				| matching results 						|			|

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
import datetime, pytz
import os, errno, sys
import pickle

START_DATE = 28
NUM_OF_DAYS = 1

def timestamp2time(timestamp):
	"""
	convert unix timestamp (int) to time str in Beijing timezone with format (%Y-%m-%d %H:%M:%S, weekday+)
	"""
	old_timezone = pytz.timezone("UTC")
	new_timezone = pytz.timezone("Asia/Chongqing")
	old_timestamp = datetime.datetime.utcfromtimestamp(timestamp)
	new_timestamp = old_timezone.localize(old_timestamp).astimezone(new_timezone)
	return new_timestamp.strftime('%Y-%m-%d %H:%M:%S')

def get_column_ids(edge, x_rn, x_cn, rw_params):
	osm_id, s_osm, t_osm = edge
	col_ids = [[osm_id, s_osm, t_osm]]
	walk_num, step_num = rw_params
	rw_res_fname = "random_walk_results_{walk_num}_{step_num}/{osm_id}_{s_osm}_{t_osm}.p".format( \
		 walk_num = walk_num, step_num = step_num, osm_id = osm_id, s_osm = s_osm, t_osm = t_osm)

	f_res = []
	b_res = []
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

	for i, (osm_id, s_osm, t_osm, _) in enumerate(f_res):
		if i > max((x_cn - 3)/2, x_cn - len(b_res) - 2):
			break
		col_ids.append([osm_id, s_osm, t_osm])

	col_ids = list(reversed(col_ids))


	for i, (osm_id, s_osm, t_osm, _) in enumerate(b_res):
		if i > max((x_cn - 3)/2, x_cn - len(f_res) - 2):
			break
		col_ids.append([osm_id, s_osm, t_osm])

	return col_ids


def gen_XY_for_one(dirname, edge, gen_XY_params, rw_params, db_params):
	osm_id, s_osm, t_osm = edge
	x_rn, x_cn, y_len, time_itv, q_rate = gen_XY_params
	rw_wn, rw_sn = rw_params
	conn, table_name = db_params
	

	fname = "{dirname}/{osm_id}_{s_osm}_{t_osm}.p".format( \
		dirname = dirname, osm_id = osm_id, s_osm = s_osm, t_osm = t_osm)
	if os.path.isfile(fname):
		return

	Xs = []
	Ys = []

	# read in edge_ids from random walk results
	# if random walk result does not have enough rows, 
	col_ids = get_column_ids(edge, x_rn, x_cn, rw_params)
	if not col_ids:
		return
	
	beginning = 1477929600 + (START_DATE - 1) * 24*60*60 # 2016/11/01 00:00:00
	cur = conn.cursor()

	for i in range(60*24*NUM_OF_DAYS/time_itv - x_cn - y_len + 1):
		print i
		start_t = beginning + i * 60 * time_itv

		
		X = []
		Y = []
		X_missing_element_num = 0
		Y_missing_element_num = 0

		# build Y
		Y_start_t = start_t + (x_cn + 0) * 60 * time_itv
		Y_end_t = start_t + (x_cn + y_len) * 60 * time_itv - 1

		for j in range(y_len):
			ele_start_t = start_t + (x_cn + j) * 60 * time_itv
			ele_end_t = ele_start_t + 60 * time_itv

			stmt = "SELECT AVG(speed) FROM {table_name} WHERE osm_id = {osm_id} AND source_osm = {s_osm} AND target_osm = {t_osm} \
				AND timestamp >= {ele_start_t} AND timestamp < {ele_end_t}".format( \
				table_name = table_name, osm_id = osm_id, s_osm = s_osm, t_osm = t_osm, \
				ele_start_t = ele_start_t, ele_end_t = ele_end_t)
			cur.execute(stmt)
			avg_speed = cur.fetchone()[0]

			if avg_speed is None:
				avg_speed = -1
				Y_missing_element_num += 1

			Y.append(avg_speed)

		if Y_missing_element_num >= y_len * (1 - q_rate):
			print "Not enough element for Y of edge {}-{}-{} during {} - {} ({} - {})".format(\
				osm_id, s_osm, t_osm, timestamp2time(Y_start_t), timestamp2time(Y_end_t), Y_start_t, Y_end_t)
			continue

		ori_osm_id, ori_s_osm, ori_t_osm = osm_id, s_osm, t_osm

		# build X
		exists_empty_row = False
		X_start_t = start_t
		X_end_t = start_t + x_cn * 60 * time_itv - 1

		for osm_id, s_osm, t_osm in col_ids:

			row = []
			row_missing_element_num = 0

			for k in range(x_cn):
				col_start_t = start_t + k * 60 * time_itv
				col_end_t = col_start_t + 60 * time_itv

				stmt = "SELECT AVG(speed) FROM {table_name} WHERE osm_id = {osm_id} AND source_osm = {s_osm} AND target_osm = {t_osm} \
					AND timestamp >= {col_start_t} AND timestamp < {col_end_t}".format( \
					table_name = table_name, osm_id = osm_id, s_osm = s_osm, t_osm = t_osm, \
					col_start_t = col_start_t, col_end_t = col_end_t)
				cur.execute(stmt)
				avg_speed = cur.fetchone()[0]

				if avg_speed is None:
					avg_speed = -1
					X_missing_element_num += 1
					row_missing_element_num += 1

				row.append(avg_speed)

			if row_missing_element_num == x_cn:
				exists_empty_row = True
				break

			X.append(row)

		if exists_empty_row:
			print "When creating X, empty row of edge {}-{}-{} during {} - {} ({} - {})".format(\
				osm_id, s_osm, t_osm, timestamp2time(X_start_t), timestamp2time(X_end_t), X_start_t, X_end_t)
			continue

		if X_missing_element_num >= x_rn * x_cn * (1 - q_rate):
			print "Not enough element for X of edge {}-{}-{} during {} - {} ({} - {})".format(\
				ori_osm_id, ori_s_osm, ori_t_osm, timestamp2time(X_start_t), timestamp2time(X_end_t), X_start_t, X_end_t)
			continue

		Xs.append(X)
		Ys.append(Y)

	if len(Xs):
		assert len(Xs) == len(Ys)
		with open(fname, 'w') as f:
		    pickle.dump([Xs,Ys], f)
			


def gen_XY_for_all(argv):
	# process input argv
	argv += [None] * 11
	x_rn 		= 11 	if argv[0] is None else int(argv[0])
	x_cn 		= 4 	if argv[1] is None else int(argv[1])
	y_len 		= 2 	if argv[2] is None else int(argv[2])
	time_itv 	= 15 	if argv[3] is None else int(argv[3])
	q_rate 		= 0.75 	if argv[4] is None else float(argv[4])
	rw_wn 		= 100 	if argv[5] is None else int(argv[5])
	rw_sn 		= 10 	if argv[6] is None else int(argv[6])
	uri 		= "host=localhost port=5432 dbname=step1 user=tom password=myPassword" \
						if argv[7] is None else argv[7]
	table_name	= "edge_speed" \
						if argv[8] is None else argv[8]

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
	conn = psycopg2.connect(uri)
	db_params = (conn, table_name)

	stmt = "SELECT DISTINCT osm_id, source_osm, target_osm FROM {table_name}".format(table_name = table_name)
	cur = conn.cursor()
	cur.execute(stmt)

	for i, edge in enumerate(cur):
		if i%10 == 9:
			print "processed {} egdes".format(i + 1)
		# Without reason, gid is in the format "(gid,)", so I use gid[0] below
		gen_XY_for_one(dirname, edge, gen_XY_params, rw_params, db_params)

	conn.close()


if __name__ == '__main__':
	gen_XY_for_all(sys.argv[1:])