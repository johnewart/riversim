from PIL import Image 
from math import log 
from numpy import * 
import pprint

def histeq(im,nbr_bins=256):

   #get image histogram
   imhist,bins = histogram(im.flatten(),nbr_bins,normed=True)
   cdf = imhist.cumsum() #cumulative distribution function
   cdf = 255 * cdf / cdf[-1] #normalize

   #use linear interpolation of cdf to find new pixel values
   im2 = interp(im.flatten(),bins[:-1],cdf)

   return im2.reshape(im.shape), cdf

img = Image.open("sm0714n0436e.tiff").convert('L')
#imdata = array(img)
#im,cdf = histeq(imdata)
#normalized = Image.fromstring("L", img.size, imdata.tostring())
#normalized.save("sm0714n0436e-grey.tif")

width = img.size[0]
height = img.size[1]

output = Image.new("L", (width, height))

histogram = img.histogram()
total_pixels = width * height

# for each pixel 
# calculate entropy for the pixel and its neighbors:
max_entropy = 0.0 
outvalues = [[0]*height for y in xrange(width)]
for x in range(1,width-1):
    print "X: %d/%d" % (x, width-1)
    for y in range(1, height-1):
        pixel = img.getpixel((x,y))
        surrounding = []
        h = 0
    
        for xoff in range(-1,2):
            for yoff in range(-1,2):
                pxx = x + xoff
                pxy = y + yoff
                otherpixel = img.getpixel((pxx, pxy))
                surrounding.append(otherpixel)
        
        avg = sum(surrounding) / len(surrounding)
        pXi = float(histogram[avg]) / float(total_pixels)
        pXi += .0001
        h += (pXi) * log2(pXi)
        print "AVG: %d" % (avg)
        #for i in range(0,254):
        #    #pXi = float(histogram[i]) / float(total_pixels)
        #    #pX  = float(histogram[avg]) / float(total_pixels)
            
        h = -1 * h
        if h > max_entropy: 
            max_entropy = h
            
        print "X: %d Y: %d h: %.5f" % (x, y, h)
        outvalues[x][y] = h
        
scalefactor = 255.0 / max_entropy
print "Scale: %.4f" % (scalefactor)
for x in range(1, width-1):
    for y in range(1, height-1):
        outputvalue = int(outvalues[x][y] * scalefactor)
        if outputvalue > 128:
            output.putpixel((x,y), 255 )
        else:
            output.putpixel((x,y), 0)

    
output.save("sm0714n0436e-entropy.tif")
        
        

#h = -E(1..N)p(Xi)log2p(X)
#H = -E(1..N)(1/255)*log2(1/255)
#N = number of gray levels
#p = probability mass function of X