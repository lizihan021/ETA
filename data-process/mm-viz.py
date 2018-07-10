#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# this file is used to convert GPS data to map_matching data
# useage: step1-viz.py gps_file max_line point_flag 
import sys

count = 0
max_line = 600

if __name__ == "__main__":
    if len(sys.argv) != 4:

    res = []
    print("conv ...")
    res_str = ""
    old_order_id = ""
    with open("gps_20161106", 'r') as f:
        for line in f:
            count += 1 
            if count > max_line:
                break
            tmp = line[:-1].split(",")
            if tmp[1] == old_order_id or count == 1:
                res_str += "{:.5f}".format(float(tmp[3]) - 0.0026) + " " + "{:.5f}".format(float(tmp[4]) + 0.0023) + "\n"
                old_order_id = tmp[1]
            else:
                f_w = open(old_order_id + ".json", 'w')
                f_w.write(res_str)
                f_w.close()
                res_str = "{:.5f}".format(float(tmp[3]) - 0.0026) + " " + "{:.5f}".format(float(tmp[4]) + 0.0023) + "\n"
                old_order_id = tmp[1]

