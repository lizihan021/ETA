#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# this file is used to convert GPS data to GPX data
# useage: step1-viz.py gps_file max_line point_flag=1 geo_flag=1 path_flag=1 
import sys
sys.path.append('../')
import gpxpy
import gpxpy.gpx
# from  gpxpy import gpx
import datetime
import subprocess
import os

count = 0
max_line = 6000

lon_off = -0.0025
lat_off = 0.0024

# Creating a new file:
# --------------------
gpx = gpxpy.gpx.GPX()
# Create first track in our GPX:
gpx_track = gpxpy.gpx.GPXTrack()
gpx.tracks.append(gpx_track)
# Create first segment in our GPX track:
gpx_segment = gpxpy.gpx.GPXTrackSegment()
gpx_track.segments.append(gpx_segment)

json_content = []

if __name__ == "__main__":
    res = []
    print("conv ...")
    gpsfilename = "Data/gps_" + sys.argv[1]
    output_folder = "output_data/" + sys.argv[1] + "/"
    try:
        subprocess.call(['mkdir', output_folder])
    except:
        pass
    res_str = ""
    old_order_id = ""

    totallinenum = 0
    with open(gpsfilename, 'r') as f:
        for line in f:
            totallinenum += 1

    print 'total line num: ', totallinenum
    print ""
    print ""

    line_idx = 0
    with open(gpsfilename, 'r') as f:
        for line in f:
            line_idx += 1
            # print_str = "\r{0}/{1} {2:.3f}%".format(line_idx, totallinenum, 100.0*float(line_idx)/float(totallinenum))
            # sys.stdout.write(print_str)
            # sys.stdout.flush()
            # count += 1 
            # if count > max_line:
            #     break
            tmp = line[:-1].split(",")
            if tmp[1] == old_order_id or count == 1:
                gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(float(tmp[4]) + lat_off, float(tmp[3]) + lon_off, time=datetime.datetime.fromtimestamp(int(tmp[2])) ))
                old_order_id = tmp[1]
                json_content.append("{0:.6f} {1:.6f} {2}\n".format(float(tmp[3])+ lon_off,float(tmp[4])+ lat_off, int(tmp[2])))
            else:
                f_json = open(output_folder + old_order_id + ".json", 'w')
                f_json.write("".join(json_content))
                f_json.close()

                f_w = open(output_folder + old_order_id + ".gpx", 'w')
                f_w.write(gpx.to_xml())
                f_w.close()

                gpx = gpxpy.gpx.GPX()
                # Create first track in our GPX:
                gpx_track = gpxpy.gpx.GPXTrack()
                gpx.tracks.append(gpx_track)
                # Create first segment in our GPX track:
                gpx_segment = gpxpy.gpx.GPXTrackSegment()
                gpx_track.segments.append(gpx_segment)
                gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(float(tmp[4]) + lat_off, float(tmp[3]) + lon_off, time=datetime.datetime.fromtimestamp(int(tmp[2])) ))
                old_order_id = tmp[1]
                json_content = ["{0:.6f} {1:.6f} {2}\n".format(float(tmp[3])+ lon_off,float(tmp[4])+ lat_off, int(tmp[2]))]

