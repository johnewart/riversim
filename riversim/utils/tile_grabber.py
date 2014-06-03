from seamlessServer import *
import sys # To accept command line arguments
import os
import subprocess
import math
import getopt
import re # Regular expression matching
import random
import string

import gdal2xyz

ned3={
    'name':'ned3',
    'servURL':'http://extract.cr.usgs.gov/Website/distreq/RequestSummary.jsp?',
    #'prodCode':'ND302XT',
    'prodCode': 'ND301HT',
    'destVar':'ZSF',
    'units':'meters',
    'description':'National Elevation Dataset 1/3 arcsecond resolution.',
    'tilesize':'1300'}



def trueLatToCorners(x, y, width, height):
    try:
        (x, y, width, height) = (float(x), float(y), float(width), float(height))
    except:
        printError("All bounds must be numbers")       
    latMin = y - (height / 2)
    latMax = y + (height / 2)
    lonMin = x - (width / 2)
    lonMax = x + (width / 2)
    return (latMin, latMax, lonMin, lonMax)

def grabData(lidar_tile_name, center_x, center_y, width, height):    
    maxDomainArea = 0.1 # A domain with a larger area than this will be 
    dataDef     = BaseDataDef(**ned3)
    dataDef.setParent(dict)
    # Extract info about data source
    srcName     = dataDef.getSourceName()
    srcDesc     = dataDef.getSourceDescription()
    srcServer   = dataDef.getServer()
    srcProd     = dataDef.getProductCode()
    outDir      = lidar_tile_name
    domX        = center_x
    originalX   = domX # For use later (index file) if domX is changed
    domY        = center_y
    originalY   = domY # For use later (index file) if domY is changed
    domWidth    = width # square width in degrees
    domHeight   = height # square height in degrees
    startX      = domX - domWidth/2.0
    startY      = domY - domWidth/2.0

    # But what if we have a really large domain? It may be too much to grab at once... let's split it up!
    divisions = 1
    while (domHeight*domWidth>maxDomainArea): # default: 0.25
        (domHeight, domWidth) = (domHeight/2.0, domWidth/2.0)
        divisions*=2

    boundsQueue=[]
    totalDlsNeeded = divisions * divisions
    dlCounter = 1

    for i in range (0,divisions):
        for j in range (0,divisions):
            # Calculate new X and Y values
            domX = startX + i*domWidth + domWidth/2.0
            domY = startY + j*domHeight + domHeight/2.0
            (latMin,latMax,lonMin,lonMax) = trueLatToCorners(domX,domY,domWidth,domHeight)
            # Create bounds
            curBounds=LatLonBounds(latMax,latMin,lonMax,lonMin)
            boundsQueue.append((curBounds, i, j)) # push calculated bounds onto the queue

    while len(boundsQueue) > 0:
        boundsTuple = boundsQueue.pop()
        bounds = boundsTuple[0]
        offX = boundsTuple[1]
        offY = boundsTuple[2]

        if divisions > 1: # Print info about how many file downloads are needed for the domain
            print("Grabbing tile %i of %i"%(dlCounter,totalDlsNeeded))
            dlCounter+=1

        # Print info about domain
        print("Bounds:")
        print("\tLatMax: %s N" % bounds.latmax)
        print("\tLatMin: %s N" % bounds.latmin)
        print("\tLonMax: %s E" % bounds.lonmax)
        print("\tLonMin: %s E" % bounds.lonmin)
        print("") # Blank line

        # Choose output directories
        print( "Output directory for all data: "+outDir+"\n")
        outGeoDir = outDir


        srcServer.misc = ''
        baseURL = srcServer.getBaseURL()
        if re.search("\w|\d", srcDesc) != None:
            print("Data source: " + srcDesc+"\n")
        print("Data Source ID: " + srcName+"\n")    
        print("Server: " + baseURL+"\n")

        URL = srcServer.getURL(srcProd, bounds) # Full URL to download page
        print("Page URL: " + URL+"\n")

        foundData = False
        while not foundData:
            try:
                dataURL = srcServer.getDataURL(URL) # .tgz file
                foundData = True
            except:
                pass

        print("Data URL: " + dataURL+"\n")

        files = srcServer.getData(srcProd, bounds, targetdir=outDir, proj='lfnative')
        print( "\nArc Data File file found:\n\t" + files[0]+"\n")

        arcdatafile = files[0] 
        xyzfile = "%s/elevation.xyz" % (outDir)
        print "Converting ARC Data File: %s to XYZ file: %s" % (arcdatafile, xyzfile)
        gdal2xyz.gdal2xyz(arcdatafile, xyzfile)
       
        sql_file   = "%s/elevation_insert.sql" % (outDir)
        sql_insert = open(sql_file, 'wb')
        sql_insert.write("set client_min_messages = 'warning';\n")
        sql_insert.write('DROP TABLE IF EXISTS elevation;\n')
        sql_insert.write('CREATE TABLE elevation ( the_geom geometry, elevation float);\n')

        xyzdata = open(xyzfile, 'r')
        for line in xyzdata:
            conv = 1.0/0.3048
            (lon, lat, elevation) = line.split(" ")
            elevation = float(elevation) * conv
            sql_insert.write("INSERT INTO elevation VALUES (geomfromtext('POINT(' || %s || ' ' || %s || ')', 4326), %s);\n" % (lon, lat, elevation))

        sql_insert.close()
        xyzdata.close()
        
        
if __name__ == "__main__":
    main()
