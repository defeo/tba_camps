from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
import views, models
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('', 
    url(r'^$', RedirectView.as_view(url='/tba/')),
    url(r'^index-tba.htm$', RedirectView.as_view(url='/tba/presentation.htm')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^tba/inscriptions\.htm$', views.InscriptionFormView.as_view(), name='inscription_form'),
    url(r'^tba/inscriptions\.htm/(?P<slug>[\w-]{22})/', include(patterns('inscription.views',
        url(r'^$', views.InscriptionView.as_view(), name='inscription_view'),
        url(r'^fiche/$', views.InscriptionPDFView.as_view(), name='inscription_pdf_view'),
        *models.urls
    ))),
    url(r'^tba/cherche.htm$', views.ReminderView.as_view(), name='inscription_reminder'),
    url(r'^tba/date\.htm$', views.pratique, name='pratique'),
    url(r'^tba/$', views.static_page, kwargs={'page' : 'index'}, name='static_index'),
    url(r'^tba/(?P<page>[a-zA-Z-_]+)\.htm$', views.static_page, name='static_pages'),
)

