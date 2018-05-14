from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.main, name='main'),
    url(r'^parse$', views.parse, name='parse'),
    url(r'^feed$', views.feed, name='feed'),
    url(r'^kml$', views.kml, name='kml'),
    url(r'^users$', views.json, name='json'),
]

