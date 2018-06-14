#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# this file is used to convert GPS data to deck.gl data


count = 0
max_line = 600

if __name__ == "__main__":
    res = []
    print("conv ...")
    f_w = open("path_psql.json", 'w')
    res_str = ""
    with open("gps_20161106", 'r') as f:
        for line in f:
            count += 1 
            if count > max_line:
                break
            tmp = line[:-1].split(",")

            res_str += "{:.5f}".format(float(tmp[3]) - 0.0026) + " " + "{:.5f}".format(float(tmp[4]) + 0.0023) + "\n"

    f_w.write(res_str)
    f_w.close()
