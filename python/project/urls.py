from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
#admin.autodiscover()

from project.terkeph.views import *

urlpatterns = patterns('',
    url(r'^$', main, name='main'),
    url(r'^heatmap$', heatmap, name='heatmap'),
    url(r'^parse$', parse, name='parse'),
    url(r'^feed$', feed, name='feed'),
    url(r'^kml$', kml, name='kml'),
    url(r'^users$', json, name='json'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

#    url(r'^[\w_]+')
)
