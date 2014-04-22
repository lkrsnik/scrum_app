from django.conf.urls import patterns, url
from scrumko import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^register/$', views.register, name='register'),
	url(r'^home/$', views.home, name='home'),
	url(r'^logout/$', views.user_logout, name='logout'),
	url(r'^sprintcreate/$', views.sprintcreate, name='spcreate'),
	url(r'^projectcreate/$', views.projectcreate, name='prcreate'),
	url(r'^maintainuser/$', views.maintainuser, name='maintainuser'),
	url(r'^maintainsprint/$', views.maintainsprint, name='maintainsprint'),
	url(r'^storycreate/$', views.storycreate, name='storycreate'),
	url(r'^maintainproject/$', views.maintainproject, name='maintainproject'),
	url(r'^edit/$', views.edit, name='edit'),
	url(r'^poker/$', views.poker, name='planing_poker')	,
	url(r'^poker_table/$', views.poker_table, name='poker_table')	,
	url(r'^poker_estimate/$', views.poker_estimate, name='poker_estimate')	,
	url(r'^poker_disactivate/$', views.poker_disactivate, name='poker_disactivate')	,
	url(r'^poker_activate/$', views.poker_activate, name='poker_activate')	,
	url(r'^poker_uselast/$', views.poker_uselast, name='poker_uselast')	,
	url(r'^pokerstart/(?P<user_story_id>\w+)/$', views.startpoker, name='startpoker')
	)
