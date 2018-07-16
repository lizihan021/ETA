import sys
import psycopg2
import pgr_utils as pgr
import path2json as p2j

# take command input python pgr_astar.py x1 y1 x2 y2
# give stdout print of edge_id


def main():
    db_name = "routing"
    username = "lingfeng"
    password = "myPassword"  

    # x1, y1 = 104.08175,30.67946
    # x2, y2 = 104.05346,30.67108
    try:
        x1, y1, x2, y2 = sys.argv[1:]
    except:
        print "commandline input error, should input x1, y1, x2, y2\n"
        exit(-1)
    
    path = pgr.get_path(db_name, username, password, x1, y1, x2, y2)

    # save edge information to file
    path_file = open("path_seq", "w")
    for edge in path:
        path_file.write("%s %s %s\n"%(edge.start_x, edge.start_y, edge.edge_cost)) 
    path_file.close()
    # save path information to json
    p2j.path2json("../../data-process/frontend-path/path-template.json", "../../data-process/frontend-path/astarpath.json", path)

if __name__ == "__main__":
    main()