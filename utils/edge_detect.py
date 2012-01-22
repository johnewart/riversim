import sys 
from liblas import file as lasfile
from liblas import vlr
from liblas import header as lasheader
from pyproj import * 
from scipy.stats import stats
import Image, ImageDraw


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
    greyscale(sys.argv[1], sys.argv[2]) 