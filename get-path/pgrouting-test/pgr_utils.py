import sys
import psycopg2

class path_edge:
    def __init__(self, gid, x1, y1, x2, y2, cost=0):
        self.edge_id = gid
        self.start_x, self.start_y = x1, y1
        self.end_x, self.end_y = x2, y2
        self.edge_cost = cost


    
def connect_db(db_name, user, password):
    try:
        conn = psycopg2.connect(database=db_name, user=user, host='localhost', password=password)
        return conn
    except:
        print "Fail to connect database", db_name

def find_nearest_vertex_id(cur, lon, lat):
    sql = """SELECT * FROM ways_vertices_pgr
        ORDER BY the_geom <-> ST_GeometryFromText('Point(%s %s)', 4326)
        LIMIT 1;""" % (lon, lat)
    cur.execute(sql)
    row = cur.fetchall()[0]
    id = row[0]
    return id

def find_path(cur, start_node, end_node):
    sql = """ 
            SELECT * FROM 
            pgr_aStar('SELECT gid AS id, source, target, cost, x1, y1, x2, y2 FROM ways', 
            (%s), (%s), directed:=true, heuristic:=3);""" % (start_node, end_node)
    cur.execute(sql)

    rows = cur.fetchall()
    path = []
    for row in rows:
        edge_id = row[3]
        if edge_id == -1:
            # reach the end node
            break
        else:
            # query the gps coordinates of the edge
            sql = "SELECT gid, source, target, x1, y1, x2, y2, cost FROM ways where gid=(%s)" % edge_id
            cur.execute(sql)
            edge_row = cur.fetchall()[0]
            # print edge_row[1], 
            [start_x, start_y, end_x, end_y, cost] = edge_row[3:]
            # add the edge information in the path
            path.append(path_edge(edge_id, start_x, start_y, end_x, end_y, cost))
    return path

def get_path(db_name, username, password, x1, y1, x2, y2):
    # connect to db
    conn = connect_db(db_name, username, password)
    cur = conn.cursor()

    # find nearest vertex
    start_node = find_nearest_vertex_id(cur, x1, y1)
    end_node = find_nearest_vertex_id(cur, x2, y2)
    # print start_node, end_node

    # find path using A*
    path = find_path(cur, start_node, end_node)
    # path_id = []
    # for edge in path:
    #     path_id.append(edge.edge_id)
    
    return path