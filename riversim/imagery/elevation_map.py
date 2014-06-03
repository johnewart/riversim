from riversim.models import *


def generate(simulation_id, force_creation = False):
  simulation = Simulation.objects.get(pk = simulation_id)

  geotiff_image = simulation.aerial_geotiff
  channel_image = simulation.channel_image
  width_image = simulation.channel_width_image

  if (not os.path.isfile(width_image)) or force_creation == True :
    logging.debug("Channel width image %s doesn't exist, generating..." % (channel_image))

    if simulation.channel_width_job_handle and force_creation == False:
      logging.debug("Job handle: %s already exists, not re-queueing" % (simulation.channel_width_job_handle))
      return None
    else:
        run_parameters = {
           'channel_image' : simulation.channel_image,
           'channel_width_image' : simulation.channel_width_image,
           'points': simulation.channel_width_points, 
           'natural_width': simulation.channel_width_natural_width, 
           'natural_height': simulation.channel_width_natural_height
        }

        client = GearmanClient(settings.GEARMAN_SERVERS)
        jobdata = json.dumps(run_parameters)
        jobrequest = client.submit_job('channel_width', jobdata, background=True)
            
        simulation.channel_width_job_handle = jobrequest.gearman_job.handle
        simulation.channel_width_job_complete = False
        simulation.save()

        return None
  else:
    img = Image.open(width_image)
    return img


