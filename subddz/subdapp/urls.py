from django.conf.urls import patterns, include, url

from subdapp import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'subddz.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
	url(r'^$', views.index, name='index'),
	url(r'^db/api/clear/$', views.clear, name='clear'),
	url(r'^db/api/user/create/$', views.user_create, name='user_create'),
)
