from django.conf.urls import patterns, url
from scrumko import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'))
