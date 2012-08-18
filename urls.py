from django.conf.urls.defaults import patterns, include, url
from django.contrib.gis import admin
from django.conf import settings

import riversim

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'riversim.views.rivers.home', name='home'),
    url(r'^riversim/', include('riversim.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', 
         {'document_root': settings.STATIC_ROOT, 'show_indexes':True}), 

)
