from django.conf.urls.defaults import patterns,  url, include
from django.contrib import admin
admin.autodiscover()
from rec import views

urlpatterns = patterns('',
	 url(r'^admin/', include(admin.site.urls)),
	 url(r'^$', views.start),
	 url(r'^signup/$', views.signup), 
	 url(r'^initial/$', views.initial),
	 url(r'^(?P<name>\d+)/$',views.home),
	 url(r'^(?P<name>\d+)/movie/$',views.movie),
	 url(r'^profile/(?P<userId>\d+)/$',views.profile),
   	 url(r'^changepassword/(?P<usersId>\d+)/$',views.changepassword),
   	 url(r'^confirm/(?P<usersId>\d+)/$',views.confirm),
	 url(r'^(?P<uId>\d+)/movie/Recommend/$', views.movieRec),
	 
)
