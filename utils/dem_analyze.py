import sys 
from liblas import file as lasfile
from liblas import vlr
from liblas import header as lasheader
from pyproj import * 
from scipy.stats import stats

from numpy import *
import Image, ImageDraw
import ImageFilter
import scipy
import mahotas 
import numpy
from scipy.stats.mstats import mquantiles

def analyze_dem(infile, outfile):
    f = open(infile,'r')
    
    # Projections for converting between the two
    #utmproj = Proj(init="epsg:26910")
    utmproj = Proj(r'+proj=utm +zone=10 +datum=NAD83 +units=us-ft +no_defs')
    latproj = Proj(proj='latlong',datum='WGS84')
    # Conversion from feet to meters
    conv = 1.0/0.3048

    tile_width = int(f.readline().split(" ")[1])
    tile_height = int(f.readline().split(" ")[1])
    xllcorner = float(f.readline().split(" ")[1])
    yllcorner = float(f.readline().split(" ")[1])
    cellsize = float(f.readline().split(" ")[1])
    nodata_value = int(f.readline().split(" ")[1])
    img = Image.new("RGB", (tile_width, tile_height))

    elevations = numpy.zeros((tile_height, tile_width))

    print "Image size: %d x %d" % (tile_width, tile_height)

    row = 0
    for line in f:
    	col = 0
    	points = line.split(" ")
    	for point in points:
    		pt = float(point)
    		if pt != nodata_value:
    			elevations[row][col] = pt
    		col += 1
    	row += 1

    # Get a reasonable max height
    min_height = mquantiles(elevations, [0.05,])[0]
    
    print "Min height: %s" % (min_height)

if __name__ == '__main__': 
    #greyscale(sys.argv[1], sys.argv[2]) 
    #extract_water(sys.argv[1], sys.argv[2])
    analyze_dem(sys.argv[1], sys.argv[2])