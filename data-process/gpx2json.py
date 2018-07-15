import gpxpy
import gpxpy.gpx
import os, sys


def gpxTojson(gpxfilename):
    # Parsing an existing file:
    # -------------------------
    gpx_file = open(gpxfilename, 'r')

    filename_list = gpxfilename.split('.')
    filename = ".".join(filename_list[:-1])
    json_name = filename + '.json'
    # print json_name

    gpx = gpxpy.parse(gpx_file)
    try:
        os.remove(json_name)
    except OSError:
        pass
        
    with open(json_name, 'a') as f:
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    f.write('{0} {1}\n'.format(point.longitude, point.latitude))
                    # print point.time
                    # print 'Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation)
    f.close()

if __name__ == '__main__':
    print len(sys.argv)
    if len(sys.argv) != 2:
        print("usage: python random_walk.py filename.gpx")
        sys.exit()
    gpxTojson(sys.argv[1]);