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
import threading

START_DATE = 1
NUM_OF_DAYS = 1
MAX_THREAD_NUM = 2
MAX_NO_DATA_TIME = 1 # unit is hour

def timestamp2time(timestamp):
	"""
	convert unix timestamp (int) to time str in Beijing timezone with format (%Y-%m-%d %H:%M:%S, weekday+)
	"""
	old_timezone = pytz.timezone("UTC")
	new_timezone = pytz.timezone("Asia/Chongqing")
	old_timestamp = datetime.datetime.utcfromtimestamp(timestamp)
	new_timestamp = old_timezone.localize(old_timestamp).astimezone(new_timezone)
	return new_timestamp.strftime('%Y-%m-%d %H:%M:%S')

def get_row_ids(edge, x_rn, x_cn, rw_params):
	osm_id, s_osm, t_osm = edge
	row_ids = [[osm_id, s_osm, t_osm]]
	walk_num, step_num = rw_params
	rw_res_fname = "random_walk_results_{walk_num}_{step_num}/{osm_id}_{s_osm}_{t_osm}.p".format( \
		 walk_num = walk_num, step_num = step_num, osm_id = osm_id, s_osm = s_osm, t_osm = t_osm)

	f_res = []
	b_res = []
	try:
		f = open(rw_res_fname)
	except IOError:
		print_str = 'Cannot open random walk result file: {}!!!\n'.format(rw_res_fname)
		sys.stdout.write(print_str)
		sys.stdout.flush()
		return [], None
	else:
		with f:
			f_res, b_res = pickle.load(f)

	# check if we get enough rows
	if len(f_res) + len(b_res) + 1 < x_rn:
		print_str = 'Random walk result file: {} does not have enough neighbor edges!!!\n'.format(rw_res_fname)
		sys.stdout.write(print_str)
		sys.stdout.flush()
		return [], None

	for i, (osm_id, s_osm, t_osm, _) in enumerate(f_res):
		if i > max((x_cn - 3)/2, x_cn - len(b_res) - 2):
			break
		row_ids.append([osm_id, s_osm, t_osm])

	row_ids = list(reversed(row_ids))
	ori_edge_id = i


	for i, (osm_id, s_osm, t_osm, _) in enumerate(b_res):
		if i > max((x_cn - 3)/2, x_cn - len(f_res) - 2):
			break
		row_ids.append([osm_id, s_osm, t_osm])

	return row_ids, ori_edge_id


# datalist is 1-D data list whose missing element should be None
# max_cont_missing_num is the maximum number of elements that are continually missing
def impute_list(datalist, max_cont_missing_num):
	valid_ele_idxs = [i for i, val in enumerate(datalist) if val != None]

	# all elements are None
	if not valid_ele_idxs:
		return datalist

	prev_valid_ele_idx = None

	new_datalist = list(datalist)

	for valid_ele_idx in valid_ele_idxs:
		if prev_valid_ele_idx is None:
			if valid_ele_idx > 0 and valid_ele_idx <= max_cont_missing_num:
				new_datalist[:valid_ele_idx] = [datalist[valid_ele_idx]] * valid_ele_idx
		else:
			# linear interpolation
			if prev_valid_ele_idx + 1 < valid_ele_idx and valid_ele_idx - prev_valid_ele_idx < max_cont_missing_num + 2:
				start_val = datalist[prev_valid_ele_idx]
				end_val = datalist[valid_ele_idx]
				incre = float(end_val - start_val)/(valid_ele_idx - prev_valid_ele_idx)
				for i in range(1, valid_ele_idx - prev_valid_ele_idx):
					new_datalist[prev_valid_ele_idx + i] = start_val + i * incre

		prev_valid_ele_idx = valid_ele_idx

	if valid_ele_idx + 1 < len(datalist) and valid_ele_idx + max_cont_missing_num + 1 >= len(datalist):
		new_datalist[valid_ele_idx + 1:] = [datalist[valid_ele_idx]] * (len(datalist) - valid_ele_idx - 1)

	return new_datalist


def gen_XY_for_one(dirname, edge, gen_XY_params, rw_params, db_params, cv):
	osm_id, s_osm, t_osm = edge
	x_rn, x_cn, y_len, time_itv, q_rate = gen_XY_params
	rw_wn, rw_sn = rw_params
	uri, table_name = db_params

	print_str = "gen XY for edge {}-{}-{}\n".format(osm_id, s_osm, t_osm)
	sys.stdout.write(print_str)
	sys.stdout.flush()

	conn = psycopg2.connect(uri)	

	fname = "{dirname}/{osm_id}_{s_osm}_{t_osm}.p".format( \
		dirname = dirname, osm_id = osm_id, s_osm = s_osm, t_osm = t_osm)
	if os.path.isfile(fname):
		cv.acquire()
		cv.notify()
		cv.release()
		return

	# read in edge_ids from random walk results
	# if random walk result does not have enough rows, 
	row_ids, ori_edge_id = get_row_ids(edge, x_rn, x_cn, rw_params)
	if not row_ids:
		cv.acquire()
		cv.notify()
		cv.release()
		return
	
	beginning = 1477929600 + (START_DATE - 1) * 24*60*60 # 2016/11/01 00:00:00
	cur = conn.cursor()

	rows_speed = []
	for row_osm_id, row_s_osm, row_t_osm in row_ids:

		row_speed = []

		for i in range(60*24*NUM_OF_DAYS/time_itv):

			start_t = beginning + i * 60 * time_itv
			end_t = start_t + 60 * time_itv

			stmt = "SELECT AVG(speed) FROM {table_name} WHERE osm_id = {osm_id} AND source_osm = {s_osm} AND target_osm = {t_osm} \
					AND timestamp >= {start_t} AND timestamp < {end_t}".format( \
					table_name = table_name, osm_id = row_osm_id, s_osm = row_s_osm, t_osm = row_t_osm, \
					start_t = start_t, end_t = end_t)
			cur.execute(stmt)

			# avg_speed can be None
			avg_speed = cur.fetchone()[0]
			row_speed.append(avg_speed)

		row_speed = impute_list(row_speed, MAX_NO_DATA_TIME * 60 / time_itv)
		rows_speed.append(row_speed)

	print_str = "Got rows_speed for edge {}-{}-{}\n".format(osm_id, s_osm, t_osm)
	sys.stdout.write(print_str)
	sys.stdout.flush()


	Xs = []
	Ys = []
	for i in range(60*24*NUM_OF_DAYS/time_itv - x_cn - y_len + 1):
		start_t = beginning + i * 60 * time_itv
		Y_start_t = start_t + (x_cn + 0) * 60 * time_itv
		Y_end_t = start_t + (x_cn + y_len) * 60 * time_itv - 1
		X_start_t = start_t
		X_end_t = start_t + x_cn * 60 * time_itv - 1
		
		X = []
		Y = []
		X_missing_element_num = 0
		Y_missing_element_num = 0

		for j in range(y_len):
			avg_speed = rows_speed[ori_edge_id][i + x_cn + j]

			if avg_speed is None:
				avg_speed = -1
				Y_missing_element_num += 1

			Y.append(avg_speed)

		if Y_missing_element_num >= y_len * (1 - q_rate):
			print_str = "Not enough element for Y of edge {}-{}-{} during {} - {} ({} - {})\n".format(\
				osm_id, s_osm, t_osm, timestamp2time(Y_start_t), timestamp2time(Y_end_t), Y_start_t, Y_end_t)
			sys.stdout.write(print_str)
			sys.stdout.flush()
			continue

		# build X
		exists_empty_row = False

		for j, (row_osm_id, row_s_osm, row_t_osm) in enumerate(row_ids):

			row = []
			row_missing_element_num = 0

			for k in range(x_cn):
				avg_speed = rows_speed[j][i + k]

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
			print_str = "When creating X, empty row of edge {}-{}-{} during {} - {} ({} - {})\n".format( \
				row_osm_id, row_s_osm, row_t_osm, \
				timestamp2time(X_start_t), timestamp2time(X_end_t), X_start_t, X_end_t)
			sys.stdout.write(print_str)
			sys.stdout.flush()
			continue

		if X_missing_element_num >= x_rn * x_cn * (1 - q_rate):
			print_str = "Not enough element for X of edge {}-{}-{} during {} - {} ({} - {})\n".format(\
				osm_id, s_osm, t_osm, timestamp2time(X_start_t), timestamp2time(X_end_t), X_start_t, X_end_t)
			sys.stdout.write(print_str)
			sys.stdout.flush()
			continue

		Xs.append(X)
		Ys.append(Y)

	# if len(Xs):
	# 	assert len(Xs) == len(Ys)
	with open(fname, 'w') as f:
		pickle.dump([Xs,Ys], f)

	cv.acquire()
	cv.notify()
	cv.release()
			


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
	uri 		= "host=localhost port=5432 dbname=routing user=tom password=myPassword" \
						if argv[7] is None else argv[7]
	table_name	= "edge_speed" \
						if argv[8] is None else argv[8]
	e_table_name	= "step1_ways" \
						if argv[9] is None else argv[9]

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
	print_str = "results are stored in dir: {dirname}\n".format(dirname = dirname)
	sys.stdout.write(print_str)
	sys.stdout.flush()

	# fetch all edge ids from psql
	conn = psycopg2.connect(uri)
	db_params = (uri, table_name)

	stmt = "SELECT osm_id, source_osm, target_osm FROM {table_name}".format(table_name = e_table_name)
	cur = conn.cursor()
	cur.execute(stmt)

	cv = threading.Condition()

	for i, edge in enumerate(cur):
		# if i%10 == 9:
		# 	print "processed {} egdes".format(i + 1)
		# Without reason, gid is in the format "(gid,)", so I use gid[0] below
		cv.acquire()
		while (threading.active_count() > MAX_THREAD_NUM):
			cv.wait()

		print_str = "\n\n\n\nstart the {}th thread\n\n\n\n".format(i)
		sys.stdout.write(print_str)
		sys.stdout.flush()

		th = threading.Thread(target=gen_XY_for_one, args=(dirname, edge, gen_XY_params, rw_params, db_params, cv, ))
		th.start()

		cv.release()

	conn.close()


if __name__ == '__main__':
	gen_XY_for_all(sys.argv[1:])