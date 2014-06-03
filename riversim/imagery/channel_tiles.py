import logging

from gearman import GearmanClient

from riversim.models import *


def generate(simulation_id, force_creation = False):
  simulation = Simulation.objects.get(pk = simulation_id)

  geotiff_image = simulation.aerial_geotiff
  channel_image = simulation.channel_image

      
  if (not os.path.isfile(channel_image)) or force_creation == True:

    if simulation.channel_tile_job_handle and force_creation == False:
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


