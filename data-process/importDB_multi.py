"""
import the txt files into the database routing, the table name is edge_speed

Usage:
    python importDB.py filename.txt

In each database entry is stored as
gid | osm_id  | timestamp | speed | source_osm | target_osm | source | target |
int | int     | int       | float | int        | int        | int    | int    |
1   | 5131313 | 2016-11-


"""

import psycopg2
import os, errno, sys
from importDB import importDB

maxthreadnum = 32

if __name__ == '__main__':
    # print len(sys.argv)
    if len(sys.argv) < 2:
        print("usage: python importDB.py filename.gpx")
        sys.exit()
    num_files = len(sys.argv) - 1
    print "number of files to convert:", num_files
    for i in range(num_files):
        print_str = "\r{0}/{1} {2:.3f}%".format(i+1, num_files, 100.0*float(i+1)/float(num_files))
        sys.stdout.write(print_str)
        sys.stdout.flush()
        while (threading.active_count() > maxthreadnum):
            time.sleep(1)
        th = threading.Thread(target=importDB, args=(sys.argv[1 + i], ))
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