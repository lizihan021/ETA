'''

CREATE TABLE public.edge_speed (
    gid bigint NOT NULL,
    "timestamp" bigint,
    speed double precision,
    source bigint NOT NULL,
    target bigint NOT NULL,
    order_id character varying(64) NOT NULL
);

'''

import psycopg2
import threading
import time

def get_distinct_key():
    # fetch all (osm id, source osm, target osm) from psql
    uri         = "host=localhost port=5432 dbname=routing user=tom password=myPassword"
    result = {};
    conn = psycopg2.connect(uri)
    table_name  = "edge_speed"
    stmt = "SELECT DISTINCT osm_id, source_osm, target_osm FROM {table_name}".format(table_name = table_name)
    cur = conn.cursor()
    cur.execute(stmt)
    file = open("distrinct.data", "w")
    for i, edge in enumerate(cur):
        if i%10 == 9:
            print "processed {} egdes".format(i + 1)
        file.write("{}_{}_{}\n".format(edge[0],edge[1],edge[2]))
    file.close()
    conn.close()

def create_table():
    uri = "host=localhost port=5432 dbname=routing user=tom password=myPassword"
    conn = psycopg2.connect(uri)
    file = open("distrinct.data", "r")
    file_line = []
    for i, line in enumerate(file):
        file_line.append(line)
    for i, line in enumerate(file_line):
        stmt = '''CREATE TABLE edge{} (
                    "timestamp" bigint,
                    speed double precision
                );\n'''.format(line)
        if i%1000 == 9:
            print stmt
        cur = conn.cursor()
        cur.execute(stmt)
        conn.commit()
    conn.close()

def saperate_table():
    uri = "host=localhost port=5432 dbname=routing user=tom password=myPassword"
    conn = psycopg2.connect(uri)
    stmt = "select osm_id, timestamp, speed, source_osm, target_osm from edge_speed_3;"
    cur = conn.cursor()
    cur.execute(stmt)
    conn.commit()
    for i, (osm_id, timestamp, speed, source_osm, target_osm) in enumerate(cur):
        if i%10000 == 9:
            print "processed {} egdes".format(i + 1)
        stmt = "INSERT into edge{}_{}_{} (timestamp, speed) VALUES ({},{});"\
                .format(osm_id, source_osm, target_osm, timestamp, speed)
        cur = conn.cursor()
        cur.execute(stmt)
        conn.commit()
    conn.close()

def clean_table():
    uri = "host=localhost port=5432 dbname=routing user=tom password=myPassword"
    conn = psycopg2.connect(uri)
    file = open("distrinct.data", "r")
    for i, line in enumerate(file):
        if i%1000 == 9:
            print "processed {} egdes".format(i + 1)
        insert_name = "edge"+line
        stmt = "DELETE FROM {};".format(insert_name)
        cur = conn.cursor()
        cur.execute(stmt)
        conn.commit()
    conn.close()

def drop_table():
    uri = "host=localhost port=5432 dbname=routing user=tom password=myPassword"
    conn = psycopg2.connect(uri)
    file = open("distrinct.data", "r")
    for i, line in enumerate(file):
        if i%1000 == 9:
            print "processed {} egdes".format(i + 1)
        insert_name = "edge"+line
        stmt = "DROP TABLE {};".format(insert_name)
        cur = conn.cursor()
        cur.execute(stmt)
        conn.commit()
    conn.close()


if __name__ == "__main__":
    #get_distinct_key()
    #drop_table()
    #create_table()
    #clean_table()
    saperate_table()










