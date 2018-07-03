import sys
import psycopg2
import pgr_utils as pgr

# 1.5127347 42.5008908 1.5135468 42.5019335

def main():
    db_name = "routing"
    username = "lingfeng"
    password = "myPassword"  
    # x1, y1 = 1.5127347, 42.5008908
    # x2, y2 = 1.5135468, 42.5019335
    x1, y1, x2, y2 = sys.argv[1:]
    path_id = pgr.get_path(db_name, username, password, x1, y1, x2, y2)

    for edge_id in path_id:
        print edge_id,

if __name__ == "__main__":
    main()