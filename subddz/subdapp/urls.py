from django.conf.urls import patterns, include, url

from subdapp import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'subddz.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
	url(r'^$', views.index, name='index'),
	url(r'^db/api/clear/$', views.clear, name='clear'),
	url(r'^db/api/status/$', views.status, name='status'),
	url(r'^db/api/user/create/$', views.user_create, name='user_create'),
	url(r'^db/api/user/details/$', views.user_details, name='user_details'),
	url(r'^db/api/user/follow/$', views.user_follow, name='user_follow'),
	url(r'^db/api/user/updateProfile/$', views.user_updateProfile, name='user_updateProfile'),
	url(r'^db/api/forum/create/$', views.forum_create, name='forum_create'),
	url(r'^db/api/forum/details/$', views.forum_details, name='forum_details'),
	url(r'^db/api/thread/create/$', views.thread_create, name='thread_create'),
	url(r'^db/api/thread/details/$', views.thread_details, name='thread_details'),
	url(r'^db/api/post/create/$', views.post_create, name='post_create'),

)
