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

gps_error = 0.000001

FNULL = open(os.devnull, 'w')

def get_insert_query(gid, osm_id, timestamp, speed, source_osm, target_osm, source, target):
    stmt = "INSERT INTO edge_speed(gid, osm_id, timestamp, speed, source_osm, target_osm, source, target) VALUES"
    stmt += "({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7});".format(gid, osm_id, timestamp, speed, source_osm, target_osm, source, target)

    return stmt

def importDB(filename, cunn):

    cur = conn.cursor()
    with open(filename,'r') as f:
        for line in f:
            gid, osm_id, timestamp, speed, source_osm, target_osm, source, target, direction = line.split()
            stmt = ""
            if int(direction):
                stmt = get_insert_query(gid, osm_id, timestamp, speed, source_osm, target_osm, source, target)
            else:
                stmt = get_insert_query(gid, osm_id, timestamp, speed, target_osm, source_osm, target, source)
            # print stmt

            try:
                cur.execute(stmt)
            except:
                print "exist!", filename
                continue
            # print cur.statusmessage
    # print "before commit"
    conn.commit()
    # print cur.statusmessage



if __name__ == '__main__':
    # print len(sys.argv)
    if len(sys.argv) < 2:
        print("usage: python importDB.py filename.gpx")
        sys.exit()
    num_files = len(sys.argv) - 1
    print "number of files to convert:", num_files

    uri = "host=localhost port=5432 dbname=routing user=umjmcb"
    conn = psycopg2.connect(uri)
    

    for i in range(num_files):
        importDB(sys.argv[1 + i], conn);
        print_str = "\r{0}/{1} {2:.3f}%".format(i+1, num_files, 100.0*float(i+1)/float(num_files))
        sys.stdout.write(print_str)
        sys.stdout.flush()

    conn.close()