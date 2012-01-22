from liblas import file as lasfile
from liblas import vlr
from liblas import header as lasheader
from pyproj import * 
from xml.dom.minidom import parseString

import httplib
import random 

import tile_grabber
import psycopg2
import sys

conn_string = "host='localhost' dbname='sanjoaquin_river' user='jewart' password=''"
try:
	pgconn = psycopg2.connect(conn_string)
	cursor = pgconn.cursor()
	print "Connected to PostgreSQL!\n"
except:
	exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()


def elevation_by_sql(lon, lat): 
    query = "select elevation from elevation where the_geom && st_buffer( geomfromtext('POINT(%(longitude).12f %(latitude).12f)', 4326) , 0.0002) order by distance(the_geom,  geomfromtext('POINT(%(longitude).12f %(latitude).12f)', 4326) ) limit 1" %  {"longitude": lon, "latitude": lat}
    #print "Query: %s" % (query)
    cursor = pgconn.cursor()
    cursor.execute(query)
    result = cursor.fetchone()
    if result != None:
        elevation = float(str(result[0]))
        return elevation
    else:
        print "Unable to find a close match for %.12f, %.12f" % (lon, lat)
        return None

def elevation_by_usgs(lon, lat):
    url = "/xmlwebservices2/elevation_service.asmx/getElevation?X_Value=%(longitude).8f&Y_Value=%(latitude).8f&Elevation_Units=FEET&Source_Layer=NED.CONUS_NED&Elevation_Only=TRUE" % {"longitude": lon, "latitude": lat}
    conn.request("GET", url)
    xmldata = conn.getresponse().read()
    dom = parseString(xmldata)
    xmltag = dom.getElementsByTagName("double")[0].toxml()
    usgs_elevation = float(xmltag.replace("<double>", "").replace("</double>", ""))
    return usgs_elevation

lidar_filename = '0712n0434e5k.las'
f = lasfile.File(lidar_filename,None,'rb')
h = f.header


conn = httplib.HTTPConnection("gisdata.usgs.gov")

# Projections for converting between the two
#utmproj = Proj(init="epsg:26910")
utmproj = Proj(r'+proj=utm +zone=10 +datum=NAD83 +units=us-ft +no_defs')
latproj = Proj(proj='latlong',datum='WGS84')
# Conversion from feet to meters
conv = 1.0/0.3048
total_diff = 0
point_count = 0
min_diff = 0.0
max_diff = 0.0
prev_diff = None

min_long, min_lat = transform(utmproj, latproj, (h.min[0] / conv), (h.min[1] / conv))
max_long, max_lat = transform(utmproj, latproj, (h.max[0] / conv), (h.max[1] / conv))

tile_width = abs(abs(max_long) - abs(min_long))
tile_height = abs(max_lat) - abs(min_lat)
center_x = min_long + (tile_width / 2.0)
center_y = min_lat  + (tile_height / 2.0)


print "Min long / lat: %.8f, %.8f" % (min_long, min_lat)
print "Max long / lat: %.8f, %.8f" % (max_long, max_lat)
print "Width: %.8f Height: %.8f" % (tile_width, tile_height)
print "Center: %.8f, %.8f" % (center_x, center_y)
target_dir = lidar_filename.split(".")[0]
#tile_grabber.grabData(target_dir, center_x, center_y, tile_width, tile_height)

total_points = f.__len__()

sample_points = random.sample(xrange(total_points), 50000)
differences = []

for index in sample_points:
    p = f[index]
    plon, plat = transform(utmproj, latproj, (p.x / conv), (p.y / conv))
    usgs_elevation = elevation_by_sql(plon, plat)

    if usgs_elevation == None:
        continue

    diff = usgs_elevation - p.z
    differences.append(diff)
    
    total_diff += abs(diff)
    point_count += 1
    avg_diff = total_diff / point_count
    min_diff = min(diff, prev_diff)
    max_diff = max(diff, prev_diff)
    print "Point: %.14f, %.14f - Z: %.4f USGS: %.4f DIFF: %f (%f)" % (plon, plat, p.z, usgs_elevation, diff, avg_diff)    
    prev_diff = diff

print "Min diff: %f / Max diff: %f" % (min_diff, max_diff)
