from django.conf.urls.defaults import patterns, include, url
from rec import views
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
urlpatterns = patterns('',
   url(r'^$', views.start),
   url(r'^signup/$', views.signup),
   url(r'^(?P<uId>\d+)/$', views.initial),
   url(r'^(?P<uId>\d+)/home/$',views.home),
   url(r'^(?P<uId>\d+)/profile/$',views.change_password),
   url(r'^(?P<uId>\d+)/movie/$',views.movie),
   url(r'^admin/', include(admin.site.urls)),
)
