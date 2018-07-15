#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# this file is used to convert GPS data to map_matching data
# useage: step1-viz.py gps_file max_line point_flag=1 geo_flag=1 path_flag=1
import sys

if __name__ == "__main__":
    with open("9f2f5a3972df52464e93495dbd528c80_result.json", 'r') as f:
        f_w = open("goodgeopoints", 'w')
        for line in f:
            line = line.strip()
            nums = line.split(" ")
            first = ", ".join(nums[0:2])
            second = "\\n".join(nums[2:4])
            w_str = "{\n\t\"type\":\"Feature\",\n\t"
            w_str += "\"geometry\": {\n\t\t\"type\": \"Point\",\n\t\t"
            w_str += "\"coordinates\": "
            w_str += "[" + first + "]\n\t},\n\t"
            w_str += "\"properties\": {\n\t\t\"titles\": \""
            w_str += second
            w_str += "\"\n\t}\n},\n"
            f_w.write(w_str)
        f_w.close()


    with open("9f2f5a3972df52464e93495dbd528c80.json", 'r') as f:
        f_w = open("goodpoints", 'w')
        for line in f:
            line = line.strip()
            newline = line.replace(" ", ",")
            f_w.write("[" + newline + "],\n")
        f_w.close()

