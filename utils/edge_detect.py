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

def gaussian_grid(size = 5):
    """
    Create a square grid of integers of gaussian shape
    e.g. gaussian_grid() returns
    array([[ 1,  4,  7,  4,  1],
           [ 4, 20, 33, 20,  4],
           [ 7, 33, 55, 33,  7],
           [ 4, 20, 33, 20,  4],
           [ 1,  4,  7,  4,  1]])
    """
    m = size/2
    n = m+1  # remember python is 'upto' n in the range below
    x, y = mgrid[-m:n,-m:n]
    # multiply by a factor to get 1 in the corner of the grid
    # ie for a 5x5 grid   fac*exp(-0.5*(2**2 + 2**2)) = 1
    fac = exp(m**2)
    g = fac*exp(-0.5*(x**2 + y**2))
    return g.round().astype(int)

class GAUSSIAN(ImageFilter.BuiltinFilter):
    name = "Gaussian"
    gg = gaussian_grid(5).flatten().tolist()
    filterargs = (5,5), sum(gg), 0, tuple(gg)


# Uses hashes of tuples to simulate 2-d arrays for the masks. 
def get_prewitt_masks(): 
    xmask = {} 
    ymask = {} 
 
    xmask[(0,0)] = -1 
    xmask[(0,1)] = 0 
    xmask[(0,2)] = 1 
    xmask[(1,0)] = -1 
    xmask[(1,1)] = 0 
    xmask[(1,2)] = 1 
    xmask[(2,0)] = -1 
    xmask[(2,1)] = 0 
    xmask[(2,2)] = 1 
 
    ymask[(0,0)] = 1 
    ymask[(0,1)] = 1 
    ymask[(0,2)] = 1 
    ymask[(1,0)] = 0 
    ymask[(1,1)] = 0 
    ymask[(1,2)] = 0 
    ymask[(2,0)] = -1 
    ymask[(2,1)] = -1 
    ymask[(2,2)] = -1 
    return (xmask, ymask)


def prewitt(pixels, width, height): 
    xmask, ymask = get_prewitt_masks() 

    # create a new greyscale image for the output 
    outimg = Image.new('L', (width, height)) 
    outpixels = list(outimg.getdata()) 

    for y in xrange(height): 
        for x in xrange(width): 
            sumX, sumY, magnitude = 0, 0, 0 

            if y == 0 or y == height-1: magnitude = 0 
            elif x == 0 or x == width-1: magnitude = 0 
            else: 
                for i in xrange(-1, 2): 
                    for j in xrange(-1, 2): 
                        # convolve the image pixels with the Prewitt mask, approximating &#8706;I / &#8706;x 
                        sumX += (pixels[x+i+(y+j)*width]) * xmask[i+1, j+1] 

                for i in xrange(-1, 2): 
                    for j in xrange(-1, 2): 
                        # convolve the image pixels with the Prewitt mask, approximating &#8706;I / &#8706;y 
                        sumY += (pixels[x+i+(y+j)*width]) * ymask[i+1, j+1] 

            # approximate the magnitude of the gradient 
            magnitude = abs(sumX) + abs(sumY)

            if magnitude > 255: magnitude = 255 
            if magnitude < 0: magnitude = 0 

            outpixels[x+y*width] = 255 - magnitude 

    outimg.putdata(outpixels) 
    return outimg

def intensity(pixel):
    r = pixel[0]
    g = pixel[1]
    b = pixel[2]
    i = (r + g + b) / 3
    return int(i)

def close_enough(src, dst):
    i1 = intensity(src)
    i2 = intensity(dst)
    diff = float(abs(i2 - i1)) / i1
    threshold = 0.0 

    if (i2 < i1): 
        threshold = 0.06
    else:
        threshold = 0.06

    print "Position %d,%d - dst: %d / src: %d (%.8f)" % (dst[0], dst[1], i2, i1, diff)

    if diff <= threshold:
        return True
    else:
        return False

def extract_river(infile, outfile, startx, starty):
    img = Image.open(infile)
    imgwidth = img.size[0]
    imgheight = img.size[1]
    outimg = Image.new("RGB", (imgwidth, imgheight))

    from collections import deque
   #import set

    d = deque()
    oi = intensity(img.getpixel((startx, starty)))     
    pt = (startx,starty)
    d.appendleft(pt)
    visited = set()
    wanted = set()
    visited.add(pt)
    wanted.add(pt)
    while(len(d) != 0):
        root = d.pop()
        oi = intensity(img.getpixel(root))
        print "Visiting %d,%d" % (root[0], root[1])
        for xoffset in xrange(-1,2):
            for yoffset in xrange(-1,2):
                neighbor = (root[0] + xoffset, root[1] + yoffset)
                if (neighbor[0] > 0 and neighbor[0] < imgwidth and neighbor[1] > 0 and neighbor[1] < imgheight):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        if close_enough(img.getpixel(root), img.getpixel(neighbor)):
                            d.appendleft(neighbor)
                            wanted.add(neighbor)
                    
    for point in visited:
        outimg.putpixel(point, (255,255,255))

    outimg.save(outfile)
 
def lidar_profile(infile, outfile):
    f = lasfile.File(infile,None,'rb')
    h = f.header

    # Projections for converting between the two
    #utmproj = Proj(init="epsg:26910")
    utmproj = Proj(r'+proj=utm +zone=10 +datum=NAD83 +units=us-ft +no_defs')
    latproj = Proj(proj='latlong',datum='WGS84')
    # Conversion from feet to meters
    conv = 1.0/0.3048

    tile_width = int(h.max[0] - h.min[0]) + 1
    tile_height = int(h.max[1] - h.min[1]) + 1
    height_offset = h.min[2]

    img = Image.new("RGB", (tile_width, tile_height))

    print "Image size: %d x %d" % (tile_width, tile_height)
    classifications = {}
    intensities = numpy.zeros((tile_width, tile_height))
    
    print "Loading LAS file into array..."
    for point in f:
        classifications[str(point.classification)] = 1    
        intensity = 0
        #intensity = int(255 / point.classification)
        x = int(point.x - h.min[0])
        y = int(point.y - h.min[1])
    
        intensities[x][y] = intensity


    print "Filling using 3x3 window..."

    for y in xrange(2, tile_height-2):
        for x in xrange(2, tile_width-2):
            total = 0
            for xoffset in xrange(-1,2):
                for yoffset in xrange(-1,2):
                    total += intensities[x+xoffset][y+yoffset]
            if total > (255*4):
                intensities[x][y] = 255
            #average = int(total / 9)
            #intensities[x][y] = average
            
    print "Writing image..."
    for y in xrange(0, tile_height):
        for x in xrange(0, tile_width):    
            intensity = intensities[x][y]
            img.putpixel((x,y), (intensity,intensity,intensity))
   
    img.save(outfile)
    return img


def extract_water(infile, outfile):
    f = lasfile.File(infile,None,'rb')
    h = f.header

    # Projections for converting between the two
    #utmproj = Proj(init="epsg:26910")
    utmproj = Proj(r'+proj=utm +zone=10 +datum=NAD83 +units=us-ft +no_defs')
    latproj = Proj(proj='latlong',datum='WGS84')
    # Conversion from feet to meters
    conv = 1.0/0.3048

    tile_width = int(h.max[0] - h.min[0]) + 1
    tile_height = int(h.max[1] - h.min[1]) + 1
    height_offset = h.min[2]

    img = Image.new("RGB", (tile_width, tile_height))

    print "Image size: %d x %d" % (tile_width, tile_height)
    classifications = {}
    intensities = numpy.zeros((tile_width, tile_height))
    
    print "Loading LAS file into array..."
    for point in f:
        classifications[str(point.classification)] = 1    
        intensity = 0
        #intensity = int(255 / point.classification)
        x = int(point.x - h.min[0])
        y = int(point.y - h.min[1])
    
        intensities[x][y] = intensity


    print "Filling using 3x3 window..."

    for y in xrange(2, tile_height-2):
        for x in xrange(2, tile_width-2):
            total = 0
            for xoffset in xrange(-1,2):
                for yoffset in xrange(-1,2):
                    total += intensities[x+xoffset][y+yoffset]
            if total > (255*4):
                intensities[x][y] = 255
            #average = int(total / 9)
            #intensities[x][y] = average
            
    print "Writing image..."
    for y in xrange(0, tile_height):
        for x in xrange(0, tile_width):    
            intensity = intensities[x][y]
            img.putpixel((x,y), (intensity,intensity,intensity))
   
    img.save(outfile)
    return img

def edgify(im):
    print classifications.keys()
    
    print "Blurring..."

    from scipy import misc
    from scipy import ndimage

    arr = misc.fromimage(img)
    very_blurred = ndimage.gaussian_filter(arr, sigma=15)

    arr = arr.astype(numpy.uint8)
    T_rc = mahotas.rc(arr)

    print "Saving as %s" % (outfile)
    misc.imsave(outfile, T_rc) 


def greyscale(infile, outfile):
    f = lasfile.File(infile,None,'rb')
    h = f.header

    # Projections for converting between the two
    #utmproj = Proj(init="epsg:26910")
    utmproj = Proj(r'+proj=utm +zone=10 +datum=NAD83 +units=us-ft +no_defs')
    latproj = Proj(proj='latlong',datum='WGS84')
    # Conversion from feet to meters
    conv = 1.0/0.3048

    tile_width = int(h.max[0] - h.min[0]) + 1
    tile_height = int(h.max[1] - h.min[1]) + 1
    height_offset = h.min[2]

    img = Image.new("RGB", (tile_width, tile_height))

    print "Image size: %d x %d" % (tile_width, tile_height)


    zvals = []

    for point in f:
        zvals.append(point.z)
    
    # Get a reasonable max height
    max_height = stats.scoreatpercentile(zvals, 99.5)
    depth_scale = 255/(max_height - h.min[2])
    print "Computed max height (99.5 percentile): %.2f" % (max_height)
    i = 0
    for point in f:
        if point.z > max_height:
            z = max_height
        else:
            z = point.z
        
        x = int(point.x - h.min[0])
        y = int(point.y - h.min[1])
    
        intensity = 255 - int(((z - height_offset) * depth_scale))
        img.putpixel((x,y), (intensity,intensity,intensity))
    
        i += 1


    img.save(outfile)


  
if __name__ == '__main__': 
    #greyscale(sys.argv[1], sys.argv[2]) 
    #extract_water(sys.argv[1], sys.argv[2])
    extract_river(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))