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
edge_id | osm_id  | timestamp | speed | source_osm_id | target_osm_id | source | target | direction |
int     | int     | int       | float | int           | int           | int    | int    |    bool   |
1       | 5131313 | 2016-11-


"""

import psycopg2
import os, errno, sys
import random
from subprocess import call
from gpx2json import gpxTojson
import numpy as np
import time
import threading

from matching import matching

maxthreadnum = 128

if __name__ == '__main__':
    # print len(sys.argv)
    if len(sys.argv) < 2:
        print("usage: python random_walk.py filename.gpx")
        sys.exit()
    num_files = len(sys.argv) - 1
    print "number of files to convert:", num_files
    for i in range(num_files):
        print_str = "\r{0}/{1} {2:.3f}%".format(i+1, num_files, 100.0*float(i+1)/float(num_files))
        sys.stdout.write(print_str)
        sys.stdout.flush()
        while (threading.active_count() > maxthreadnum):
            time.sleep(1)
        th = threading.Thread(target=matching, args=(sys.argv[1 + i], ))
        th.start()
        print_str = "\r{0}/{1} {2:.3f}%".format(i+1, num_files, 100.0*float(i+1)/float(num_files))
        sys.stdout.write(print_str)
        sys.stdout.flush()

    print ""
    print ""
    while (threading.active_count() > 1):
        sys.stdout.write("\ralive thread: "+str(threading.active_count()-1)+" ")
        sys.stdout.flush()
        time.sleep(0.5)

    print "done!"