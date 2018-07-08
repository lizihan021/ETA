#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# this file is used to convert GPS data to deck.gl data

import json
count = 0
max_line = 600000

if __name__ == "__main__":
    res = []
    print("conv ...")
    f_w = open("path.json", 'w')
    json_item = {"vendor": 0, "segments": []}
    old_id = "-1"
    sparse = 0
    path_num = 0
    old_time = 0
    with open("gps_20161106", 'r') as f:
        for line in f:
            count += 1 
            if count > max_line:
                break
            tmp = line[:-1].split(",")
            time = int(tmp[2][6:])%1800
            seg = [str(float(tmp[3]) - 0.0026), str(float(tmp[4]) + 0.0023), str(time)]
            if (tmp[0] == old_id or old_id == "-1") and (time > old_time and time - old_time < 50):
                sparse += 1
                if sparse == 1:
                    json_item["segments"].append(seg)
                if sparse == 2:
                    sparse = 0
            else:
                sparse = 0
                path_num += 1
                res.append(json_item)
                json_item = {"vendor": 0, "segments": []}
            old_id = tmp[0]
            old_time = time

    json.dump(res, f_w, indent=2)
    print(path_num)
