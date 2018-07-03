import sys
import psycopg2

class path_edge:
    def __init__(self, gid, x1, y1, x2, y2):
        self.edge_id = gid
        self.start_x, self.start_y = x1, y1
        self.end_x, self.end_y = x2, y2
        self.edge_cost = 0


    
def connect_db(db_name, user, password):
    try:
        conn = psycopg2.connect(database=db_name, user=user, password=password)
        return conn
    except:
        print "Fail to connect database", db_name
