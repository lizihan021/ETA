from convert import ptspath_convert
import sys, os

front_end_path_dir = "frontend-path/"
path_header = "path_head.txt"
path_footer = "path_foot.txt"

front_end_points_dir = "frontend-points/"
point_header = "point_head.txt"
point_footer = "point_foot.txt"

def path_convert(in_file):
    filename = in_file.split('/')[-1]
    f_w = open(front_end_path_dir + filename, 'w')

    with open(path_header, 'r') as f:
        for line in f:
            f_w.write(line)

    with open(in_file, 'r') as f:
        flag = True
        for line in f:
            if flag:
                flag = not flag
            else:
                f_w.write(',')

            line = line.split(" ")
            newline = ",".join(line[0:2])
            f_w.write("[" + newline + "]\n")
        

    with open(path_footer, 'r') as f:
        for line in f:
            f_w.write(line)

    f_w.close()

def pts_convert(in_file):
    filename = in_file.split('/')[-1]
    f_w = open(front_end_points_dir + filename, 'w')

    with open(point_header, 'r') as f:
        for line in f:
            f_w.write(line)

    with open(in_file, 'r') as f:
        flag = True
        for line in f:
            if flag:
                flag = not flag
            else:
                f_w.write(',')

            line = line.split(" ")
            newline = ",".join(line[0:2])
            f_w.write("[" + newline + "]\n")
        

    with open(point_footer, 'r') as f:
        for line in f:
            f_w.write(line)

    f_w.close()


if __name__ == '__main__':
    # print len(sys.argv)
    if len(sys.argv) < 2:
        print("usage: python batch_convert option[point/path] *.json")
        sys.exit()
    num_files = len(sys.argv) - 2
    print "number of files to convert:", num_files

    if sys.argv[1] == "path":
        for i in range(num_files):
            path_convert(sys.argv[2 + i])
    elif sys.argv[1] == "point":
        for i in range(num_files):
            pts_convert(sys.argv[2 + i])
    # elif sys.argv[1] == "geo":
    #     for i in range(num_files):
    #         geo_convert(sys.argv[2 + i])
    else:
        print "wrong option, option = point/path"