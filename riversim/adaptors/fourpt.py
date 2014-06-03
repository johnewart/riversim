from riversim.utils.usgs import usgs_elevation
from gearman import GearmanClient
from django.conf import settings

import json

def run(simulation, run):
	rivers = simulation.rivers.all()
	start_point = simulation.start_point
	end_point = simulation.end_point
	start_elevation = usgs_elevation(start_point.x, start_point.y)
	end_elevation = usgs_elevation(end_point.x, end_point.y)
	river_length = 0 
	for river in rivers:
		river_length += river.geom.length

	# This is dumb, we need to do a proper calculation but for now this is good enough
	river_length_ft = river_length * 69.1 * 5280
	number_of_cross_sections = 1
	upstream_width = 30
	downstream_width = 30

	distance_ft = start_point.distance(end_point) * 69.1 * 5280

	channels = [
		{
			'length' : distance_ft, 
			'cross_sections' : number_of_cross_sections,
			'start_elevation' : start_elevation, 
			'end_elevation' : end_elevation,
			'upstream_width' : upstream_width, 
			'downstream_width': downstream_width
		},
	]

	model_parameters = {
		'maxtimesteps' : 80, 
		'time_step': 300, 
		'time_weight': 0.6, 
		'amplitude': 1999.5, 
		'period': 3.33, 
		'phase_angle': 1.67, 
		'start_time': 0.0, 
		'end_time': 1.667
	}

	run_parameters = {
		'channels': channels, 
		'model_parameters': model_parameters,
		'simulation_id': simulation.id, 
		'run_id': run.id
	}
	
	client = GearmanClient(settings.GEARMAN_SERVERS)
	jobdata = json.dumps(run_parameters)
	client.submit_job('fourpt', jobdata, background=True)

	return True