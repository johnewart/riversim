import re
import os
import sys
import Image
import json

import numpy
import osr
import gdal

from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.gis.geos.geometry import GEOSGeometry
from django.db.models import Q
from django.conf import settings

from utils.usgs import *

from riversim.models import *
from riversim.utils import closest_point, render_to_json

from gearman import GearmanClient

import logging, traceback

def generate(simulation_id):
  simulation = Simulation.objects.get(pk = simulation_id)

  geotiff_image = simulation.aerial_geotiff
  channel_image = simulation.channel_image

      
  if not os.path.isfile(channel_image):

    if simulation.channel_tile_job_handle:
        logging.debug("Job handle: %s already exists, not re-queueing" % (simulation.channel_tile_job_handle)) 
        return None
    else:
        logging.debug("Channel image %s doesn't exist, generating..." % (channel_image))

        run_parameters = {
          'tile_path': settings.RIVER_TILES_PATH,
          'geotiff_image': geotiff_image, 
          'channel_image': channel_image,
          'ortho_tiles': [tile.tile for tile in simulation.get_ortho_tiles()],
          'tile_width': 5000, 
          'tile_height': 5000 
        }

        client = GearmanClient(settings.GEARMAN_SERVERS)
        jobdata = json.dumps(run_parameters)
        jobrequest = client.submit_job('channel_image', jobdata, background=True)

        simulation.channel_tile_job_handle = jobrequest.gearman_job.handle
        simulation.channel_tile_job_complete = False
        simulation.save()

        return None

  else:  
    img = Image.open(channel_image)
    return img


