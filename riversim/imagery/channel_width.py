import logging

from gearman import GearmanClient

from riversim.models import *


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


