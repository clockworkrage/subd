from django.conf.urls import patterns, include, url

from subdapp import views, post, thread, forum, user

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'subddz.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
	url(r'^$', views.index, name='index'),
	url(r'^db/api/clear/$', views.clear, name='clear'),
	url(r'^db/api/status/$', views.status, name='status'),
	url(r'^db/api/user/create/$', user.user_create, name='user_create'),
	url(r'^db/api/user/details/$', user.user_details, name='user_details'),
	url(r'^db/api/user/follow/$', user.user_follow, name='user_follow'),
	url(r'^db/api/user/updateProfile/$', user.user_updateProfile, name='user_updateProfile'),
	url(r'^db/api/user/listFollowers/$', user.user_listFollowers, name='user_listFollowers'),
	url(r'^db/api/forum/create/$', forum.forum_create, name='forum_create'),
	url(r'^db/api/forum/details/$', forum.forum_details, name='forum_details'),
	url(r'^db/api/forum/listPosts/$', forum.forum_listPosts, name='forum_listPosts'),
	url(r'^db/api/thread/create/$', thread.thread_create, name='thread_create'),
	url(r'^db/api/thread/details/$', thread.thread_details, name='thread_details'),
	url(r'^db/api/thread/subscribe/$', thread.thread_subscribe, name='thread_subscribe'),
	url(r'^db/api/thread/unsubscribe/$', thread.thread_unsubscribe, name='thread_unsubscribe'),
	url(r'^db/api/thread/update/$', thread.thread_update, name='thread_update'),
	url(r'^db/api/thread/vote/$', thread.thread_vote, name='thread_vote'),
	url(r'^db/api/thread/close/$', thread.thread_close, name='thread_close'),
	url(r'^db/api/thread/open/$', thread.thread_open, name='thread_open'),
	url(r'^db/api/thread/remove/$', thread.thread_remove, name='thread_remove'),
	url(r'^db/api/thread/restore/$', thread.thread_restore, name='thread_restore'),
	url(r'^db/api/thread/list/$', thread.thread_list, name='thread_list'),
	url(r'^db/api/post/create/$', post.post_create, name='post_create'),
	url(r'^db/api/post/details/$', post.post_details, name='post_details'),
	url(r'^db/api/post/remove/$', post.post_remove, name='post_remove'),
	url(r'^db/api/post/restore/$', post.post_restore, name='post_restore'),
	url(r'^db/api/post/vote/$', post.post_vote, name='post_vote'),
	url(r'^db/api/post/update/$', post.post_update, name='post_update'),
	url(r'^db/api/post/list/$', post.post_list, name='post_list'),


)
