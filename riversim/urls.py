from django.conf.urls.defaults import *
from tastypie.api import Api
from riversim.api import *

api = Api()
api.register(SimulationResource())
api.register(ChannelMapResource())
api.register(ChannelWidthMapResource())
api.register(AerialMapResource())

urlpatterns = patterns('riversim',
    url(r'login/?$', 'views.public.do_login', name='login'),
    url(r'kml/(?P<layer>[^/]+)$', 'views.rivers.kml', name='kml'),

    # API
    url(r'api/', include(api.urls)),

    # Stations
    url(r'stations/?$', 'views.stations.list', name='list_stations'),
    url(r'stations/(?P<station_id>\d+)/?$', 'views.stations.show', name='show_station'),
    url(r'stations/(?P<station_id>\d+)/sync/?$', 'views.stations.sync', name='sync_station'),

    # Simulations
    url(r'simulations/$', 'views.simulations.list', name='list_simulations'),
    url(r'simulations/create/?$', 'views.simulations.create', name='create_simulation'),
    url(r'simulations/new/?$', 'views.simulations.new', name='new_simulation'),
    url(r'simulations/(?P<simulation_id>\d+)/step/(?P<step_name>\w+)/$', 'views.simulations.step', name='simulation_step'),
    url(r'simulations/(?P<simulation_id>\d+)/update/?$', 'views.simulations.update', name='update_simulation'),
    url(r'simulations/(?P<simulation_id>\d+)/$', 'views.simulations.show', name='show_simulation'),
    url(r'simulations/(?P<simulation_id>\d+)/edit$', 'views.simulations.edit', name='edit_simulation'),
    url(r'simulations/(?P<simulation_id>\d+)/aerial/(?P<thumbnail_width>\d+)', 'views.simulations.aerial_image_thumbnail', name='simulation_aerial_image_thumbnail'),
    url(r'simulations/(?P<simulation_id>\d+)/aerial/?', 'views.simulations.aerial_image', name='simulation_aerial_image'),
    url(r'simulations/(?P<simulation_id>\d+)/channels/(?P<thumbnail_width>\d+)', 'views.simulations.channel_image_thumbnail', name='simulation_channel_image_thumbnail'),
    url(r'simulations/(?P<simulation_id>\d+)/channels/?', 'views.simulations.channel_image', name='simulation_channel_image'), 
    url(r'simulations/(?P<simulation_id>\d+)/channel_width/(?P<thumbnail_width>\d+)', 'views.simulations.channel_width_image_thumbnail', name='simulation_channel_width_image_thumbnail'),
    url(r'simulations/(?P<simulation_id>\d+)/channel_width/?', 'views.simulations.channel_width_image', name='simulation_channel_width_image'),
    
    # Simulation runs
    url(r'simulations/(?P<simulation_id>\d+)/runs/(?P<simulation_run_id>\d+)/?$', 'views.simulations.show_run', name='show_simulation_run'),
    url(r'simulations/(?P<simulation_id>\d+)/runs/new/?$', 'views.simulations.new_run', name='new_simulation_run'),
    url(r'simulations/(?P<simulation_id>\d+)/runs/create/?$', 'views.simulations.create_run', name='create_simulation_run'),

    # Simulation Models
    url(r'models/?$', 'views.models.list', name='list_models'),
    url(r'models/(?P<model_id>\d+)/?$', 'views.models.show', name='show_model'),
    url(r'models/(?P<model_id>\d+)/edit/?$', 'views.models.edit', name='edit_model'),
    url(r'models/parameters/(?P<model_parameter_id>\d+)/edit/?$', 'views.models.edit_parameter', name='edit_model_parameter'),
    url(r'models/(?P<model_id>\d+)/parameters/create/?$', 'views.models.create_parameter', name='create_model_parameter'),

    # AJAX methods
    url(r'rivers/filter?$', 'views.rivers.filter_rivers', name='filter_rivers'),
    url(r'rivers/select/?$', 'views.rivers.select_rivers', name='select_rivers'),
    url(r'stations/sensor_names', 'views.stations.station_sensors', name='station_sensors'),
    url(r'simulations/closest_point_on_river/?', 'views.simulations.closest_point_on_river', name='closest_point_on_river'),

    # WMS
    url(r'wms/?$', 'views.public.wms', name='wms'),
)
