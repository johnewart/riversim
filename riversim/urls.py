from django.conf.urls.defaults import *

urlpatterns = patterns('riversim',
    url(r'login/?$', 'views.public.do_login', name='login'),
    url(r'stations/(?P<type>\w+)/(?P<station_id>\d+)/?$', 'views.rivers.stationdata', name='station_data'),
    url(r'filters/riversim/?$', 'views.rivers.filter_rivers', name='filter_rivers'),
    url(r'kml/(?P<layer>[^/]+)$', 'views.rivers.kml', name='kml'),

    # Simulations
    url(r'simulations/$', 'views.simulations.list', name='list_simulations'),
    url(r'simulations/create/?$', 'views.simulations.create', name='create_simulation'),
    url(r'simulations/new/?$', 'views.simulations.new', name='new_simulation'),
    url(r'simulations/(?P<simulation_id>\d+)/update/?$', 'views.simulations.update', name='update_simulation'),
    url(r'simulations/(?P<simulation_id>\d+)/?$', 'views.simulations.show', name='show_simulation'),
    url(r'simulations/(?P<simulation_id>\d+)/edit$', 'views.simulations.edit', name='edit_simulation'),
)
