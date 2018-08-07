import sys
import psycopg2
import pgr_utils as pgr
import path2json as p2j
import math
import os
import simplejson as json

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
    def __init__(self, id, s, t, c, speed, l):
        self.edge_id = id
        self.source = s
        self.target = t
        self.cost = c
        self.speed = speed
        self.length_m = l

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
        if edge.target == node.node_id:
            neighbor_id_set.append(edge.source)
    for id in neighbor_id_set:
        neighbor_set.append(map.nodes[id-1])
    return neighbor_set

def cost_of_edge(source, target, map):
    for edge in map.edges:
        if edge.source == source.node_id and edge.target == target.node_id:
            return edge.cost
        if edge.target == source.node_id and edge.source == target.node_id:
            # print "reverse"
            return edge.cost
    print "error cost"

# def h(source, goal, map, avg_speed_percent):
#     lat_diff = source.lat - goal.lat
#     lon_diff = source.lon - goal.lon
#     return math.sqrt(lat_diff*lat_diff+lon_diff*lon_diff)
def h(source, goal, map, avg_speed_percent):
    max_speed = 110 * avg_speed_percent / 3.6
    R = 6373000
    lat1 = math.radians(source.lat)
    lon1 = math.radians(source.lon)
    lat2 = math.radians(goal.lat)
    lon2 = math.radians(goal.lon)

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (math.sin(dlat/2))**2 + math.cos(lat1) * math.cos(lat2) * (math.sin(dlon/2))**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    return distance / max_speed



def astar(start, goal, map):
    closed_set = []
    open_set = []
    current = start
    open_set.append(start)
    state_count = 0 # state number for visualization
    get_node_staus_json(state_count, open_set, open_set, map)
    while open_set:
        current = min(open_set, key=lambda x:x.h+x.g)
        # print current.node_id
        state_nodes = []
        # print current.node_id
        if current.node_id == goal.node_id:
            return True
        open_set.remove(current)
        closed_set.append(current)

        # print len(neighbor(current, map))

        for node in neighbor(current, map):
            if node in closed_set:
                continue
            if node in open_set:
                new_g = current.g + cost_of_edge(current, node, map)
                if node.g > new_g:
                    node.g = new_g
                    node.parent = current
            else:
                new_g = current.g + cost_of_edge(current, node, map)
                node.g = new_g
                node.parent = current
                open_set.append(node)
                state_nodes.append(node)
        if not state_nodes:
            continue
        else:
            state_count = state_count + 1
            point_set = open_set + closed_set
            get_node_staus_json(state_count, state_nodes, point_set, map)

    print "No path found!!!"
    return False

def get_node_staus_json(state_count, state_nodes, point_set, map):
    input_json_file = "../data-process/frontend-points/pt-template1.json"

    file_in = open(input_json_file, "r")

    # load data to json_data
    json_data = json.load(file_in)

    # output json state files
    point_count = 0

    # points in set
    max_cost_node = max(point_set, key=lambda x:x.h)
    max_cost = max_cost_node.h
    # point in single file
    for point in state_nodes:
        output_json_file = "../data-process/frontend-astar/astar-pt-%d-%d.json" % (state_count, point_count)
        point_count = point_count + 1
        # name file out
        file_out = open(output_json_file, "w")
        # edit json
        coordinates = []
        coordinates.append([point.lon, point.lat])
        coordinates.append([100,30])
        json_data["source"]["data"]["geometry"]["coordinates"] = coordinates
        json_data["paint"]["circle-color"] = cost_to_rgb_code(point.h, max_cost)
        # write back json
        file_out.write(json.dumps(json_data, sort_keys=True, use_decimal=True, indent=4, separators=(',', ': ')))
        file_out.close()

    # close input file
    file_in.close()

def cost_to_rgb_code(cost, max_cost):
    if cost < max_cost/2:
        g = round(cost/(max_cost/2) * 255)
        b = 255 - g
        r = 0
    else:
        r = round((cost/(max_cost/2) - 1) * 255)
        g = 255 - r
        b = 0
    color = '#%02X%02X%02X' % (r, g, b)
    return color

def get_map(cur, t):
    # get average speed percentage of max speed for all edges
    sql = "SELECT predict_speed FROM time_%s WHERE osm_id=-1" % (t)
    cur.execute(sql)
    row = cur.fetchall()[0]
    avg_speed_percent = row[0]
    # print avg_speed_percent
    # get all edges
    sql = "SELECT gid, osm_id, source, target, maxspeed_forward, length_m, cost FROM ways"
    cur.execute(sql)
    rows = cur.fetchall()
    edges = []
    # print len(rows)
    for row in rows:
        [edge_id, edge_osm_id, source, target, maxspeed_forward, length_m, cost] = row[0:7]
        sql = "SELECT predict_speed FROM time_%s WHERE osm_id=%s" % (t, edge_osm_id)
        cur.execute(sql)
        speed_rows = cur.fetchall()
        if not speed_rows:
            speed = abs(maxspeed_forward) * avg_speed_percent / 3.6
        else:
            speed = speed_rows[0][0]
        cost = length_m / speed
        # speed = abs(maxspeed_forward) * avg_speed_percent / 3.6
        edges.append(Edge(edge_id, source, target, cost, speed, length_m))
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
    return map, avg_speed_percent

def map_initialize(end_node, map, avg_speed_percent):
    for node in map.nodes:
        node.h = h(node, end_node, map, avg_speed_percent)

def get_path(end, map):
    t = 0
    path = []
    current = end
    while current.parent!=None:
        edges = map.edges
        for edge in edges:
            if edge.source == current.node_id and edge.target == current.parent.node_id:
                edge_time = edge.length_m / edge.speed
            else:
                if edge.target == current.node_id and edge.source == current.parent.node_id:
                    edge_time = edge.length_m / edge.speed
        path.append(current)
        current = current.parent
        t += edge_time
    path.append(current)
    return path, t

def main():
    db_name = "routing"
    username = "tom"
    password = "myPassword"

    # x1, y1 = 104.08175,30.67946
    # x2, y2 = 104.05346,30.67108
    # get x, y from input
    try:
        x1, y1, x2, y2 = sys.argv[1:]
        t = 1480505400
    except:
        print "commandline input error, should input x1, y1, x2, y2, t\n"
        exit(-1)

    conn = pgr.connect_db(db_name, username, password)
    cur = conn.cursor()

    start_node_id = pgr.find_nearest_vertex_id(cur, x1, y1)
    end_node_id = pgr.find_nearest_vertex_id(cur, x2, y2)
    map, avg_speed_percent = get_map(cur, t)
    print "Finish map"
    start_node = map.nodes[start_node_id-1]
    end_node = map.nodes[end_node_id-1]

    map_initialize(end_node, map, avg_speed_percent)
    print "Finish setup"
    mydir = "../data-process/frontend-astar"
    filelist = [ f for f in os.listdir(mydir) ]
    for f in filelist:
        os.remove(os.path.join(mydir, f))
    print "Finish delete"
    is_path_exist = astar(start_node, end_node, map)
    node_list = []
    if is_path_exist:
        node_list, total_time = get_path(end_node, map)
        node_list = [elem.node_id for elem in node_list]
        node_list.reverse()
        print round(total_time/60)
    # path json
    input_json_file = "../data-process/frontend-path/path-template.json"
    output_json_file = "../data-process/frontend-path/astar-path.json"
    file_in = open(input_json_file, "r")
    file_out = open(output_json_file, "w")
    # load data to json_data
    json_data = json.load(file_in)
    path_coordinates = []
    for node_num in node_list:
        node = map.nodes[node_num-1]
        path_coordinates.append([node.lon, node.lat])
    json_data["source"]["data"]["geometry"]["coordinates"] = path_coordinates
    json_data["paint"]["line-width"] = 4
    json_data["paint"]["line-color"] = "#ef8783"
    file_out.write(json.dumps(json_data, sort_keys=True, use_decimal=True, indent=4, separators=(',', ': ')))
    file_out.close()

if __name__ == "__main__":
    main()