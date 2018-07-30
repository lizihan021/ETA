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
    for i, line in enumerate(file_line[::-1]):
        stmt = '''CREATE TABLE edge{} (
                    gid bigint NOT NULL,
                    "timestamp" bigint,
                    speed double precision,
                    source bigint NOT NULL,
                    target bigint NOT NULL,
                    order_id character varying(64) NOT NULL
                );\n'''.format(line)
        if i%1000 == 9:
            print stmt
        cur = conn.cursor()
        try:
            cur.execute(stmt)
            conn.commit()
        except:
            continue
    conn.close()

def saperate_table():
    uri = "host=localhost port=5432 dbname=routing user=tom password=myPassword"
    conn = psycopg2.connect(uri)
    stmt = "select * from edge_speed;"
    cur = conn.cursor()
    cur.execute(stmt)
    conn.commit()
    for i, (gid, osm_id, timestamp, speed, source_osm, target_osm, source, target, order_id) in enumerate(cur):
        if i%10000 == 9:
            print "processed {} egdes".format(i + 1)
        stmt = "INSERT into edge{}_{}_{} (gid, timestamp, speed, source, target, order_id) VALUES ({},{},{},{},{},'{}');"\
                .format(osm_id, source_osm, target_osm, gid, timestamp, speed, source, target, order_id)
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


if __name__ == "__main__":
    #get_distinct_key()
    #create_table()
    clean_table()
    saperate_table()










