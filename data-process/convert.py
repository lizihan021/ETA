#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
convert.py

Facilitate convertion from raw GPS data to mapbox readable style file.

WARNING: convert.py does not automatically convert to style file (JSON file),
         it only convert part of the JSON file.
"""

import sys

"""
This function converts data into geojson file.

Sample data input:
104.084655 30.656510 0 21003
104.084391 30.656630 1 21003

Sample data output:
{
    "type":"Feature",
    "geometry": {
        "type": "Point",
        "coordinates": [104.084655, 30.656510]
    },
    "properties": {
        "titles": "0\n21003"
    }
},
{
    "type":"Feature",
    "geometry": {
        "type": "Point",
        "coordinates": [104.084391, 30.656630]
    },
    "properties": {
        "titles": "1\n21003"
    }
},
"""
geo_convert(in_file):
    with open(in_file, 'r') as f:
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

"""
This function converts data into geojson file.

Sample data input:
104.084655 30.656510
104.084391 30.656630

Sample data output:
[104.08466,30.65652],
[104.08440,30.65665],
"""
ptspath_convert(in_file):
    with open(in_file, 'r') as f:
        f_w = open("goodpoints", 'w')
        for line in f:
            line = line.strip()
            newline = line.replace(" ", ",")
            f_w.write("[" + newline + "],\n")
        f_w.close()


if __name__ == "__main__":
    geo_convert("9f2f5a3972df52464e93495dbd528c80_result.json")
    ptspath_convert("9f2f5a3972df52464e93495dbd528c80.json")

