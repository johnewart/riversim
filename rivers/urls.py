from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'filters/rivers/?$', 'rivers.views.filter_rivers', name='filter_rivers'),
    url(r'kml/(?P<layer>[^/]+)$', 'rivers.views.kml', name='kml'),
)
