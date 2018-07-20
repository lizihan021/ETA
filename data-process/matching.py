"""
match the raw gps trajectory in gpx and json file, to a sequence of edges and snapped gps coordinates,
and output the speed of traversing for each edge to a file

Usage:
    python match.py filename.gpx

Example:
    python match.py mapmatching-data/25f4781b41678af45c70b80030a94a1e.gpx

Results:
    outputs for front end:
        output the sequence point of nodes that sketch the curved matched edges to a .gpx.res.json file
        output the snapped gps coodinates to a _result.json file
    output the edge speed data in a txt file, that will be used for CNN training

In each edge speed txt file, the data are stored as
gid | osm_id  | timestamp | speed | source_osm | target_osm | source | target | direction |
int | int     | int       | float | int        | int        | int    | int    |    bool   |
1   | 5131313 | 2016-11-


"""

import psycopg2
import os, errno, sys
import random
from subprocess import call
from gpx2json import gpxTojson
import numpy as np

gps_error = 0.000001

FNULL = open(os.devnull, 'w')

def get_insert_query(gid, osm_id, timestamp, speed, source_osm, target_osm, source, target, order_id):
    stmt = "INSERT INTO edge_speed(gid, osm_id, timestamp, speed, source_osm, target_osm, source, target, order_id) VALUES"
    stmt += "({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8});".format(gid, osm_id, timestamp, speed, source_osm, target_osm, source, target, order_id)

    return stmt

# datalist is 1-D data list, nullValue is the value which represent that the data is missing
def impute_list(datalist, nullValue):
    for idx in range(len(datalist)):
        if datalist[idx] == nullValue:
            if idx == 0:
                while idx < len(datalist) and datalist[idx] == nullValue:
                    idx += 1
                if idx < len(datalist):
                    datalist[:idx] = [datalist[idx]] * idx

            elif idx == len(datalist)-1:
                datalist[idx] = datalist[idx-1]

            else:
                start_idx = idx
                while idx < len(datalist) and datalist[idx] == nullValue:
                    idx += 1
                if idx < len(datalist):
                    increment = (datalist[idx] - datalist[start_idx-1])/(idx - start_idx + 1)
                    datalist[start_idx:idx] = [datalist[start_idx-1] + (i+1)*increment for i in range(idx - start_idx)]
                else:
                    datalist[start_idx:idx] = [datalist[start_idx-1]] * (idx - start_idx)

    return datalist

def get_distance_query(lon, lat, gid):
    stmt = "SELECT ST_Distance(ST_SetSRID(ST_MakePoint({0:.7f}, {1:.7f}), 4326)::geography, the_geom::geography) AS distance FROM ways WHERE gid = {2};"\
            .format(lon, lat, gid)

    return stmt

def get_location_query(lon, lat, gid):
    stmt = "SELECT ST_LineLocatePoint(the_geom, ST_SetSRID(ST_MakePoint({0:.7f}, {1:.7f}), 4326)) AS location FROM ways WHERE gid = {2};"\
            .format(lon, lat, gid)

    return stmt

def get_snapped_point_query(lon, lat, gid):
    stmt = ("SELECT ST_X( ST_ClosestPoint( the_geom, ST_SetSRID(ST_MakePoint({0:.7f}, {1:.7f}), 4326) ) ) AS clon, " + \
           "ST_Y(ST_ClosestPoint(the_geom, ST_SetSRID(ST_MakePoint({2:.7f}, {3:.7f}), 4326))) AS clat " + \
           " FROM ways WHERE gid = {4};").format(lon, lat, lon, lat, gid)

    return stmt

def get_edge_query_string(x1, y1, x2, y2):
    stmt = "SELECT gid, osm_id, source_osm, target_osm, name, length_m, source, target FROM {table_name} ".format(table_name = 'ways')
    stmt = stmt + "WHERE (x1 < {0:.7f} AND x1 > {1:.7f} AND y1 < {2:.7f} AND y1 > {3:.7f} ".format(*map(float, (x1+gps_error,x1-gps_error,y1+gps_error,y1-gps_error)))
    stmt = stmt +    "AND x2 < {0:.7f} AND x2 > {1:.7f} AND y2 < {2:.7f} AND y2 > {3:.7f}) ".format(*map(float, (x2+gps_error,x2-gps_error,y2+gps_error,y2-gps_error)))
    # stmt = stmt +    "OR (x1 < {0:.7f} AND x1 > {1:.7f} AND y1 < {2:.7f} AND y1 > {3:.7f} ".format(*map(float, (x2+gps_error,x2-gps_error,y2+gps_error,y2-gps_error)))
    # stmt = stmt +    "AND x2 < {0:.7f} AND x2 > {1:.7f} AND y2 < {2:.7f} AND y2 > {3:.7f}) ".format(*map(float, (x1+gps_error,x1-gps_error,y1+gps_error,y1-gps_error)))
    
    return stmt

def get_percent(cur, lon, lat, gid):
    stmt = get_location_query(lon, lat, gid)
    cur.execute(stmt)
    for location in cur:
        return location[0]
    return 0

def matching(filename):
    name_list = filename.split('.')
    txtname = "".join(name_list[0:-1]) + ".txt"
    if os.path.isfile(txtname):
        print txtname, " exist!"
        return
    # print filename
    # call graphopper to match the most possible sequence
    call(['java', '-jar', 'map-matching/matching-web/target/graphhopper-map-matching-web-0.11-SNAPSHOT.jar', 'match', filename], stdout=FNULL)
    # convert the match results in gpx file to json file
    gpxTojson(filename+'.res.gpx')
    gpxTojson(filename+'.edge.gpx')
    call(['rm', filename+'.res.gpx'])
    call(['rm', filename+'.edge.gpx'])
    gps_edges = []
    with open(filename+'.edge.json','r') as f:
        for line in f:
            lon, lat = line.split()
            # print i, lat, lon
            gps_edges.append([float(lon), float(lat)])

    # call(['rm', filename+'.edge.json'])
    # fetch the edges from psql with matched start node and end node
    uri = "host=localhost port=5432 dbname=routing user=tom password=myPassword"
    conn = psycopg2.connect(uri)
    cur = conn.cursor()

    edges = []
    for idx in range(len(gps_edges)-1):
        # print "\n------------------------"
        edge_candidate = []
        x1, y1 = gps_edges[idx]
        x2, y2 = gps_edges[idx+1]

        # Try to find the positive traversion
        stmt = get_edge_query_string(x1, y1, x2, y2)
        cur.execute(stmt)
        for gid, osm_id, source_osm, target_osm, name, length_m, source, target in cur:
            edge_candidate.append([gid, osm_id, source_osm, target_osm, name, length_m, source, target, 1])
            # print name
        # print idx, edge_candidate

         # Try to find the negative traversion if positive traversion doesn't exist
        if len(edge_candidate) == 0:
            stmt = get_edge_query_string(x2, y2, x1, y1)
            cur.execute(stmt)
            for gid, osm_id, source_osm, target_osm, name, length_m, source, target in cur:
                edge_candidate.append([gid, osm_id, source_osm, target_osm, name, length_m, source, target, 0])

        if len(edge_candidate) == 1:
            edges.append(edge_candidate[0])
        elif len(edge_candidate) > 1:
            # print idx, "shit!!!!!!!", len(edge_candidate)
            randnum = random.randint(0, len(edge_candidate)-1)
            edges.append(edge_candidate[randnum])

    # for i, e in enumerate(edges):
    #     print i, e[0], e[1], e[2], e[3], e[4], e[5]

    # Get raw gps data from the json file (with time stamps)
    # process the filename of json file
    raw_gps = {}
    filename_list = filename.split('.')
    filename = ".".join(filename_list[:-1])
    json_name = filename + '.json'
    idx = 0
    with open(json_name,'r') as f:
        for line in f:
            str_list = line.split()
            lon, lat, time = str_list[0], str_list[1], str_list[2]
            # print idx, lon, lat, time
            raw_gps[idx] = [float(lon), float(lat), int(time)]
            idx = idx + 1


    # query the distances from the point to the edge
    distance_mat = np.zeros((len(raw_gps), len(edges)))
    for gps_idx in range(len(raw_gps)):
        for egde_idx in range(len(edges)):
            lon, lat = raw_gps[gps_idx][0], raw_gps[gps_idx][1]
            gid = edges[egde_idx][0]
            stmt = get_distance_query(lon, lat, gid)
            cur.execute(stmt)
            for distance in cur:
                # print distance[0]
                distance_mat[gps_idx, egde_idx] = distance[0]

    best_match = np.argmin(distance_mat, axis=1)
    # for eid in best_match:
    #     print eid

    # save snapped gps point to result json file
    result_json = filename + '_result.json'
    try:
        os.remove(result_json)
    except OSError:
        pass

    with open(result_json, 'a') as f:
        for gps_idx in range(len(raw_gps)):
            lon, lat = raw_gps[gps_idx][0], raw_gps[gps_idx][1]
            gid = edges[best_match[gps_idx]][0]
            stmt = get_snapped_point_query(lon, lat, gid)
            cur.execute(stmt)
            for clon, clat in cur:
                # print "matched gps: ", gps_idx, clon, clat
                f.write('{0:.6f} {1:.6f} {2} {3}\n'.format(clon, clat, gps_idx, gid))
    f.close()

    # Do two passes on the best match to get the speed
    # First pass calculate handy available speeds
    # Second pass impute the missing data
    speeds = np.zeros(len(edges))
    prev_edge_id = None
    starttime = None
    endtime = None
    startpercent = None
    endpercent = None
    timestamps = [None] * len(edges)
    # start first pass
    for gps_idx in range(len(raw_gps)):
        # initialize
        if gps_idx == 0:
            prev_edge_id = 0
            starttime = raw_gps[gps_idx][2]
            endtime = raw_gps[gps_idx][2]
            lon, lat, gid = raw_gps[gps_idx][0], raw_gps[gps_idx][1], edges[best_match[gps_idx]][0]
            startpercent = get_percent(cur, lon, lat, gid)
            endpercent = startpercent
            timestamps[prev_edge_id] = starttime

        # cases for edge changing
        if prev_edge_id == best_match[gps_idx]:
            # print "prev_edge_id == best_match[gps_idx]", prev_edge_id, best_match[gps_idx], 's: ', starttime, 'e: ', endtime
            endtime = raw_gps[gps_idx][2]
            lon, lat, gid = raw_gps[gps_idx][0], raw_gps[gps_idx][1], edges[best_match[gps_idx]][0]
            
            # for the last point
            if gps_idx == len(raw_gps) - 1:
                dt = endtime - starttime
                if dt > 0:
                    endpercent = get_percent(cur, lon, lat, gid)
                    path_length = edges[prev_edge_id][5] #* np.abs(startpercent - endpercent)
                    speeds[prev_edge_id] = path_length/dt
                    # print prev_edge_id, 'pathlength: ', edges[prev_edge_id][5], " ,startpercent: ", startpercent, " ,endpercent: ", endpercent, " ,dt: ", dt, " ,speed: ", speeds[prev_edge_id]
            else:
                continue
        else:
            # print "prev_edge_id != best_match[gps_idx]", prev_edge_id, best_match[gps_idx]
            endtime = raw_gps[gps_idx][2]
            dt = endtime - starttime
            # print 'dt: ', dt
            if dt > 0:
                endpercent = get_percent(cur, lon, lat, gid)
                path_length = edges[prev_edge_id][5] #* np.abs(startpercent - endpercent)
                speeds[prev_edge_id] = path_length/dt
                # print prev_edge_id, 'pathlength: ', edges[prev_edge_id][5], " ,startpercent: ", startpercent, " ,endpercent: ", endpercent, " ,dt: ", dt, " ,speed: ", speeds[prev_edge_id]
            
            prev_edge_id = best_match[gps_idx]
            starttime = raw_gps[gps_idx][2]
            endtime = raw_gps[gps_idx][2]
            startpercent = get_percent(cur, lon, lat, gid)
            endpercent = startpercent
            timestamps[prev_edge_id] = starttime

    # start second pass, which imputes the missing data
    # for edge_idx in range(len(edges)):
    #     print edge_idx, speeds[edge_idx]

    # print "-------------------------------"
    speeds = impute_list(speeds, 0)

    edge_speed_file = filename + '.txt'
    order_id = filename.split('/')[-1]
    try:
        os.remove(edge_speed_file)
    except OSError:
        pass

    with open(edge_speed_file, 'a') as f:
        for edge_idx in range(len(edges)):
            e = edges[edge_idx]
            gid, osm_id, source_osm, target_osm, source, target, direction = e[0], e[1], e[2], e[3], e[6], e[7], e[8]
            if timestamps[edge_idx]:
                # print edge_idx, speeds[edge_idx], timestamps[edge_idx]
                f.write('{0} {1} {2} {3:.3f} {4} {5} {6} {7} {8}\n'\
                        .format(gid, osm_id, timestamps[edge_idx], speeds[edge_idx], source_osm, target_osm, source, target, direction))
            else:
                # print edge_idx, speeds[edge_idx], timestamps[edge_idx]
                f.write('{0} {1} {2} {3} {4} {5} {6} {7} {8}\n'\
                        .format(gid, osm_id, 0, -1, source_osm, target_osm, source, target, direction))
    
    # for idx in range(len(raw_gps)):
    #     print raw_gps[idx][0], raw_gps[idx][1], raw_gps[idx][2  ]
    conn.close()

if __name__ == '__main__':
    # print len(sys.argv)
    if len(sys.argv) < 2:
        print("usage: python random_walk.py filename.gpx")
        sys.exit()
    num_files = len(sys.argv) - 1
    print "number of files to convert:", num_files
    for i in range(num_files):
        matching(sys.argv[1 + i]);
        print_str = "\r{0}/{1} {2:.3f}%".format(i+1, num_files, 100.0*float(i+1)/float(num_files))
        sys.stdout.write(print_str)
        sys.stdout.flush()