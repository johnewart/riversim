import re
import os
import glob
import logging
import Image
import ImageFont, ImageDraw, ImageOps

import numpy
import osr
import gdal

from riversim.utils import log_traceback

def stitch_tiles(tile_files, max_image_width=None):
    min_north = None
    max_north = None
    min_east = None
    max_east = None


    for tile_file in tile_files:
        filename = tile_file.split("/")[-1]
        m = re.match(r"(\d+)n(\d+)e", filename)
        logging.debug("Filename: %s" % (tile_file))
        east  = int(m.group(2))
        north = int(m.group(1))
        min_north = north if min_north is None else min(min_north, north)
        max_north = north if max_north is None else max(max_north, north)
        min_east  = east if min_east is None else min(min_east, east)
        max_east  = east if max_east is None else max(max_east, east)

    # Open first tile and get dimensions as tile size
    try:
        #tile = Image.open(tile_files[0])
        #tile_width = tile.size[0]
        #tile_height = tile.size[1]
        tile_width = 5000
        tile_height = 5000

        logging.debug("East: %d - %d North: %d - %d" % (min_east, max_east, min_north, max_north))

        num_tiles_x = (max_east - min_east) + 1
        num_tiles_y = (max_north - min_north) + 1
        logging.debug("Tiles %d x %d" % (num_tiles_x, num_tiles_y))

        width = (num_tiles_x * tile_width)
        height = (num_tiles_y * tile_height)
 
        # Resize if needed to match width
        if max_image_width != None:
            if width > max_image_width:
                width = int(max_image_width)
                tile_width = width / num_tiles_x
                tile_height = tile_width
                height = (num_tiles_y * tile_height)

       
        logging.debug("Generating tiled image: %d x %d" % (width, height))

        final_image = Image.new("RGBA", (width, height), (0,0,0,0))
        f = ImageFont.load_default()

        imgcount = 1
        imgtotal = len(tile_files)

        for tile_file in tile_files:
            filename = tile_file.split("/")[-1]
            logging.debug("Processing (%d/%d): %s" % (imgcount, imgtotal, filename))
            m = re.match(r"(\d+)n(\d+)e", filename)
            east  = int(m.group(2))
            north = int(m.group(1))

            x = ((east - min_east)) * tile_width
            y = height - (((north - min_north) + 1) * tile_height)

            try:
                temp_image = Image.open(tile_file)
            except:
                temp_image = Image.new('RGBA', (tile_width, tile_height))

            # Resize if needed
            if tile_width != temp_image.size[0]:
                temp_image = temp_image.resize( (tile_width, tile_height), Image.BICUBIC)

            final_image.paste(temp_image, (x, y))
            imgcount = imgcount + 1

        return final_image
    except Exception, args:
        print "Can't determine tile dimensions..."
        log_traceback(Exception, args)
