from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'stations/(?P<type>\w+)/(?P<station_id>\d+)/?$', 'rivers.views.stationdata', name='station_data'),
    url(r'filters/rivers/?$', 'rivers.views.filter_rivers', name='filter_rivers'),
    url(r'kml/(?P<layer>[^/]+)$', 'rivers.views.kml', name='kml'),
)
