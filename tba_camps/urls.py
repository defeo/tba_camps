from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
import views
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('', 
    url(r'^$', RedirectView.as_view(url='/tba/')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^inscription/$', views.InscriptionView.as_view(), name='inscription'),
    url(r'^tba/$', views.static_page, kwargs={'page' : 'index'}, name='static_index'),
    url(r'^tba/(?P<page>[a-z]+)/$', views.static_page, name='static_pages'),
)
