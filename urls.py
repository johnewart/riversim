from django.conf.urls.defaults import patterns, include, url
from django.contrib.gis import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'riversim.rivers.views.home', name='home'),
    url(r'^rivers/', include('riversim.rivers.urls')),    
    (r'^admin/', include(admin.site.urls)),
)
