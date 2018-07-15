# Usage: python check_travel_time_sum.py mapmatching-data/*.txt
# input: output .txt files by matching.py
#
#


import psycopg2
import os, errno, sys
import random
from subprocess import call
from gpx2json import gpxTojson
import numpy as np

#get the length of the edge in meters
def get_edge_length(gid):
    stmt = "SELECT length_m FROM {table_name} ".format(table_name = 'ways')
    stmt = stmt + "WHERE gid = {0}".format(gid)

    uri = "host=localhost port=5432 dbname=routing user=tom password=myPassword"
    conn = psycopg2.connect(uri)
    cur = conn.cursor()
    cur.execute(stmt)

    distance = 0.0
    for length_m in cur:
        distance = length_m[0]
    conn.close()

    return distance

def check(filename):
    print "----------------------"
    print "order: ", filename
    edges = []
    with open(filename,'r') as f:
        for line in f:
            gid, _, timestamp, speed, _, _, _, _, _ = line.split()
            print gid, timestamp, speed
            edges.append([int(gid), int(timestamp), float(speed)])

    filename_list = filename.split('.')
    filename = ".".join(filename_list[:-1])
    json_name = filename + '.json'
    raw_time = []
    with open(json_name,'r') as f:
        for line in f:
            _, _, timestamp = line.split()
            raw_time.append(int(timestamp))

    ordertime = raw_time[-1] - raw_time[0]
    totaltime = 0.0
    for i, e in enumerate(edges):
        length = get_edge_length(e[0])
        print i, " , gid: ", e[0], " , length: ", length, ",speed: ", e[2], ",time: ", length/e[2]
        totaltime += length/e[2]

    print 'ordertime: ', ordertime, ", totaltime: ", totaltime


if __name__ == '__main__':
    # print len(sys.argv)
    if len(sys.argv) < 2:
        print("usage: python random_walk.py filename.gpx")
        sys.exit()
    num_files = len(sys.argv) - 1
    print "number of files to check:", num_files
    for i in range(num_files):
        check(sys.argv[1 + i]);