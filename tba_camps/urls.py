from django.conf.urls import include, url
from django.views.generic import RedirectView, TemplateView
from . import views, models, sms, ffbb_api,admin

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/tba/', permanent=True)),
    url(r'^index-tba.htm$', RedirectView.as_view(url='/tba/presentation.htm', permanent=True)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^sms/', include(sms.urls)),
    url(r'^api/ffbb/', include(ffbb_api.urls)),
    url(r'^tba/inscriptions\.htm$', views.InscriptionFormView.as_view(), name='inscription_form'),
    url(r'^tba/inscriptions\.htm/(?P<slug>[\w-]{22})/', include([
        url(r'^$', views.InscriptionView.as_view(), name='inscription_view'),
        url(r'^fiche/$', views.InscriptionPDFView.as_view(), name='inscription_pdf_view'),
    ] + models.urls)),
    url(r'^tba/cherche.htm$', views.ReminderView.as_view(), name='inscription_reminder'),
    url(r'^tba/date\.htm$', views.pratique, name='pratique'),
    url(r'^tba/$', views.static_page, kwargs={'page' : 'index'}, name='static_index'),
    url(r'^tba/(?P<page>[a-zA-Z-_]+)\.htm$', views.static_page, name='static_pages'),
]
