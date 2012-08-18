import re
import os
import sys
import Image
import json

import numpy
import osr
import gdal

from django.contrib.gis.geos.geometry import GEOSGeometry
from django.db.models import Q
from django.conf import settings

from utils.usgs import *

from riversim.models import *


import logging, traceback

def generate(simulation_id):
    tile_path = settings.RIVER_TILES_PATH
    simulation = Simulation.objects.get(pk = simulation_id)
    tiles = simulation.ortho_tiles

    img_tiles = []
    for tile in tiles:
        imgfile = "%s/%s.tif" % (tile_path, tile.tile)
        logging.debug("Tile: %s" % (tile.tile))
        img_tiles.append(imgfile)

    from utils.image_stitcher import stitch_tiles
    logging.debug("Generating aerial image with width: %d" % (settings.MAX_AERIAL_IMAGE_WIDTH))
    img = stitch_tiles(img_tiles, settings.MAX_AERIAL_IMAGE_WIDTH)

    # Also save full size image as GeoTIFF
    image_extent = tiles.extent()
    print "Extent: %s" % (str(image_extent))
    topleft = Point(image_extent[0], image_extent[3], srid=tiles[0].geom.srid)
    bottomright = Point(image_extent[2], image_extent[1], srid=tiles[0].geom.srid)
    topleft.transform(4326)
    bottomright.transform(4326)

    res_x = abs(bottomright.x - topleft.x) / img.size[0]
    res_y = abs(topleft.y - bottomright.y) / img.size[1]

    pixels = numpy.array(img)
    driver = gdal.GetDriverByName("GTiff")

    geotiff_file = simulation.aerial_geotiff
    geotiff_dir = os.path.dirname(geotiff_file)
    if(not os.path.exists(geotiff_dir)):
        os.makedirs(geotiff_dir)

    dst_ds = driver.Create(str(geotiff_file), img.size[0], img.size[1], 3, gdal.GDT_Byte)
    # SetGeoTransform [ topleft_x, pixel_width, rotation, topleft_y, rotation, pixel_height]
    dst_ds.SetGeoTransform( [ topleft.x, res_x, 0, topleft.y, 0, -res_y] )

    srs = osr.SpatialReference()
    srs.SetWellKnownGeogCS("WGS84")
    dst_ds.SetProjection( srs.ExportToWkt() )

    print "Writing GeoTIFF file %s..." % (geotiff_file)
    # write the band
    print "Channel 1 (Red)..."
    dst_ds.GetRasterBand(1).WriteArray(pixels[:,:,0])
    print "Channel 2 (Green)..."
    dst_ds.GetRasterBand(2).WriteArray(pixels[:,:,1])
    print "Channel 3 (Blue)..."
    dst_ds.GetRasterBand(3).WriteArray(pixels[:,:,2])
    #print "Channel 4 (Alpha)..."
    #dst_ds.GetRasterBand(4).WriteArray(pixels[:,:,3])

    simulation.aerialmap_width = res_x
    simulation.aerialmap_height = res_y
    simulation.save()

    return img
