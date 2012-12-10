
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

def generate(image, options, force_creation = False):
  simulation = image.simulation

  points = options['points']
  for point in points:
    logging.debug("Point: %d,%d" % (point['x'], point['y']))
  natural_width = int(options['naturalWidth'])
  natural_height = int(options['naturalHeight'])
  image.channel_width_points = json.dumps(points)
  image.image_natural_width = natural_width
  image.image_natural_height = natural_height
  image.save()

  geotiff_image = simulation.aerialmap.filname
  channel_image = simulation.channelmap.filename
  width_image = simulation.channelwidthmap.filename

  if (not os.path.isfile(width_image)) or force_creation == True :
    logging.debug("Channel width map image %s doesn't exist, generating..." % (width_image))

    if image.job_handle and force_creation == False:
      logging.debug("Job handle: %s already exists, not re-queueing" % (image.job_handle))
      return None
    else:
        run_parameters = {
           'channel_image' : simulation.channel_image,
           'channel_width_image' : simulation.channel_width_image,
           'elevation_map_image' : elevation_image
        }

        client = GearmanClient(settings.GEARMAN_SERVERS)
        jobdata = json.dumps(run_parameters)
        jobrequest = client.submit_job('elevation_map', jobdata, background=True)
            
        simulation.elevation_map_job_handle = jobrequest.gearman_job.handle
        simulation.elevation_map_job_complete = False
        simulation.save()

        return None
  else:
    img = Image.open(width_image)
    return img


