import sys
import psycopg2
import pgr_utils as pgr

# 1.5127347, 42.5008908
# 1.5135468, 42.5019335
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
            (%s), (%s), directed:=false, heuristic:=3);""" % (start_node, end_node)
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
            sql = "SELECT gid, source, target, x1, y1, x2, y2 FROM ways where gid=(%s)" % edge_id
            cur.execute(sql)
            edge_row = cur.fetchall()[0]
            [start_x, start_y, end_x, end_y] = edge_row[3:]
            # add the edge information in the path
            path.append(pgr.path_edge(edge_id, start_x, start_y, end_x, end_y))
    return path

def get_path(x1, y1, x2, y2):
    # connect to db
    db_name = "routing"
    username = "lingfeng"
    password = "myPassword"
    conn = pgr.connect_db(db_name, username, password)
    cur = conn.cursor()

    # find nearest vertex
    start_node = find_nearest_vertex_id(cur, x1, y1)
    end_node = find_nearest_vertex_id(cur, x2, y2)

    # find path using A*
    path = find_path(cur, start_node, end_node)
    path_id = []
    for edge in path:
        path_id.append(edge.edge_id)

    # see path information
    print len(path)
    # for edge in path:
    #     print "(edge id = %s, from %s, %s, to %s, %s)" % (edge.edge_id, edge.start_x, edge.start_y, edge.end_x, edge.end_y)
    
    return path_id

def main():
    x1, y1 = 1.5127347, 42.5008908
    x2, y2 = 1.5135468, 42.5019335
    path_id = get_path(x1, y1, x2, y2)
    print path_id

if __name__ == "__main__":
    main()