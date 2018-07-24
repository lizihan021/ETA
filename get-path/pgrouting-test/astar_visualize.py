import sys
import psycopg2
import pgr_utils as pgr
import path2json as p2j
import math

# take command input python pgr_astar.py x1 y1 x2 y2
# give stdout print of edge_id
class Node:
    def __init__(self, id, lon, lat):
        self.node_id = id
        self.lat = lat
        self.lon = lon
        self.parent = None
        self.g = 0
        self.h = 0

class Edge:
    def __init__(self, id, s, t, c):
        self.edge_id = id
        self.source = s
        self.target = t
        self.cost = c

class Map:
    def __init__(self, edges, nodes):
        self.edges = edges
        self.nodes = nodes

def neighbor(node, map):
    neighbor_id_set = []
    neighbor_set = []
    edges = map.edges
    for edge in edges:
        if edge.source == node.node_id:
            neighbor_id_set.append(edge.target)
    for id in neighbor_id_set:
        neighbor_set.append(map.nodes[id-1])
    return neighbor_set
def cost(source, target, map):
    for edge in map.edges:
        if edge.source == source.node_id and edge.target == target.node_id:
            return edge.cost

def h(source, goal, map):
    lon_diff = source.lon - goal.lon
    lat_diff = source.lat - goal.lat
    return math.sqrt(lon_diff*lon_diff + lat_diff*lat_diff)

def astar(start, goal, map):
    closed_set = []
    open_set = []
    current = start
    open_set.append(start)

    while open_set:
        current = min(open_set, key=lambda x:x.h+x.g)
        # print current.node_id
        if current == goal:
            return True
        open_set.remove(current)
        closed_set.append(current)

        # print len(neighbor(current, map))
        
        for node in neighbor(current, map):
            if node in closed_set:
                continue
            if node in open_set:
                new_g = current.g + cost(current, node, map)
                if node.g > new_g:
                    node.g = new_g
                    node.parent = current
            else:
                new_g = current.g + cost(current, node, map)
                node.g = new_g
                node.parent = current
                open_set.append(node)
    print "No path found!!!"
    return False


def get_map(cur):
    # get all edges
    sql = "SELECT gid, source, target, cost FROM ways"
    cur.execute(sql)
    rows = cur.fetchall()
    edges = []
    for row in rows:
        [edge_id, source, target, cost] = row[0:4]
        edges.append(Edge(edge_id, source, target, cost))
    # get all nodes
    sql = "SELECT id, lon, lat FROM ways_vertices_pgr"
    cur.execute(sql)
    rows = cur.fetchall()
    nodes = []
    for row in rows:
        [id, lon, lat] = row[0:3]
        nodes.append(Node(id, lon, lat))
    # create map
    map = Map(edges, nodes)
    # print len(map.edges), len(map.nodes)
    # return the map
    return map

def map_initialize(end_node, map):
    for node in map.nodes:
        node.h = h(node, end_node, map)

def get_path(end, map):
    path = []
    current = end
    while current.parent!=None:
        path.append(current)
        current = current.parent
    path.append(current)
    return path


def main():
    db_name = "routing"
    username = "tom"
    password = "myPassword"  

    x1, y1 = 104.08175,30.67946
    x2, y2 = 104.05346,30.67108
    # # get x, y from input
    # try:
    #     x1, y1, x2, y2 = sys.argv[1:]
    # except:
    #     print "commandline input error, should input x1, y1, x2, y2\n"
    #     exit(-1)
    
    conn = pgr.connect_db(db_name, username, password)
    cur = conn.cursor()

    start_node_id = pgr.find_nearest_vertex_id(cur, x1, y1)
    end_node_id = pgr.find_nearest_vertex_id(cur, x2, y2)
    
    map = get_map(cur)

    start_node = map.nodes[start_node_id-1]
    end_node = map.nodes[end_node_id-1]
    
    map_initialize(end_node, map)
    
    is_path_exist = astar(start_node, end_node, map)

    if is_path_exist:
        node_list = get_path(end_node, map)
        node_list = [elem.node_id for elem in node_list]
    node_list.reverse()
    print node_list
if __name__ == "__main__":
    main()