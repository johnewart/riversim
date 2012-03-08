from django.conf.urls.defaults import patterns, include, url
from django.contrib.gis import admin

import riversim

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'riversim.views.rivers.home', name='home'),
    url(r'^riversim/', include('riversim.urls')),
    (r'^admin/', include(admin.site.urls)),
)
