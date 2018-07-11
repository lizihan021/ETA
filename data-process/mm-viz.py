#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# this file is used to convert GPS data to map_matching data
# useage: step1-viz.py gps_file max_line point_flag=1 geo_flag=1 path_flag=1 
import sys

count = 0
max_line = 600

lon_off = -0.0025
lat_off = 0.0024

if __name__ == "__main__":
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
                res_str += "{:.5f}".format(float(tmp[3]) + lon_off) + " " + "{:.5f}".format(float(tmp[4]) + lat_off) + "\n"
                old_order_id = tmp[1]
            else:
                f_w = open("./mapmatching-data/" + old_order_id + ".json", 'w')
                f_w.write(res_str)
                f_w.close()
                res_str = "{:.5f}".format(float(tmp[3]) + lon_off) + " " + "{:.5f}".format(float(tmp[4]) + lat_off) + "\n"
                old_order_id = tmp[1]

