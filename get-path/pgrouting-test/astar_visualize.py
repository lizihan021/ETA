import sys
import psycopg2
import pgr_utils as pgr
import path2json as p2j

# take command input python pgr_astar.py x1 y1 x2 y2
# give stdout print of edge_id

def astar(cur, start_node, end_node):
    closed_set = []

    open_set = []

    came_from_map = []


def get_map(curr):

    # sql = """ 
    #         SELECT * FROM 
    #         pgr_aStar('SELECT gid AS id, source, target, cost, x1, y1, x2, y2 FROM ways', 
    #         (%s), (%s), directed:=true, heuristic:=3);""" % (start_node, end_node)
    cur.execute(sql)

def main():
    db_name = "routing"
    username = "tom"
    password = "myPassword"  

    # x1, y1 = 104.08175,30.67946
    # x2, y2 = 104.05346,30.67108
    try:
        x1, y1, x2, y2 = sys.argv[1:]
    except:
        print "commandline input error, should input x1, y1, x2, y2\n"
        exit(-1)
    
    conn = pgr.connect_db(db_name, username, password)
    cur = con.cursor()

    start_node = find_nearest_vertex_id(cur, x1, y1)
    end_node = find_nearest_vertex_id(cur, x2, y2)

    astar(cur, start_node, end_node)


if __name__ == "__main__":
    main()