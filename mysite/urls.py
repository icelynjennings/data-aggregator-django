from django.conf.urls import patterns, include, url
from django.contrib import admin

from aggr import views

from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = patterns('',
    # Examples:
	

	# General urls
	url(r'^$', 'aggr.views.home', name='home'),
	url(r'^login/$', 'aggr.views.user_login', name='user_login'),
	url(r'^logout/$', 'aggr.views.user_logout', name='user_logout'),
	url(r'^profile/(?P<type>[-_\w]+)/(?P<pid>[-_\w]+)/$', 'aggr.views.profile', name='profile'),
	url(r'^profile/(?P<type>[-_\w]+)/(?P<pid>[-_\w]+)/(?P<mode>[-_\w]+)/$', 'aggr.views.profile', name='profile'),
	url(r'^register/$', 'aggr.views.register', name='register'),
	url(r'^admin/', include(admin.site.urls)),
	
	url(r'^json/MediaItem/', views.MediaItemList.as_view()),	
	
	# Media item urls
	url(r'^(?P<itemtype>[-_\w]+)/$', 'aggr.views.media_list'),
	url(r'^(?P<itemtype>[-_\w]+)/(?P<name>[-_\w]+)/$', 'aggr.views.media_item'),
	url(r'^(?P<itemtype>[-_\w]+)/(?P<name>[-_\w]+)/reviews$', 'aggr.views.item_reviews'),
	url(r'^(?P<itemtype>[-_\w]+)/(?P<name>[-_\w]+)/userreviews$', 'aggr.views.item_userreviews'),
	

	
	
)

urlpatterns = format_suffix_patterns(urlpatterns)