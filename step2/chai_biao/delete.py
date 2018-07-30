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

def drop_table():
    uri = "host=localhost port=5432 dbname=routing user=tom password=myPassword"
    conn = psycopg2.connect(uri)
    file = open("distrinct.data", "r")
    for i, line in enumerate(file):
        if i%1000 == 9:
            print "processed {} egdes".format(i + 1)
        insert_name = "edge"+line
        stmt = "DELETE FROM {} WHERE speed > 50;".format(insert_name)
        cur = conn.cursor()
        cur.execute(stmt)
        conn.commit()
    conn.close()


if __name__ == "__main__":
    #get_distinct_key()
    drop_table()
    #create_table()
    #clean_table()
    #saperate_table()










