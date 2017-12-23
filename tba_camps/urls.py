from django.urls import include, path
from django.views.generic import RedirectView, TemplateView
from . import views, models, sms, ffbb_api,admin

urlpatterns = [
    path(r'', RedirectView.as_view(url='/tba/', permanent=True)),
    path(r'index-tba.htm', RedirectView.as_view(url='/tba/presentation.htm', permanent=True)),
    path(r'admin/', admin.site.urls),
    path(r'sms/', include(sms.urls)),
    path(r'tba/inscriptions.htm', views.InscriptionFormView.as_view(), name='inscription_form'),
    path(r'tba/inscriptions.htm/<slug:slug>/', include([
        path(r'', views.InscriptionView.as_view(), name='inscription_view'),
        path(r'fiche/', views.InscriptionPDFView.as_view(), name='inscription_pdf_view'),
    ] + models.urls)),
    path(r'tba/cherche.htm', views.ReminderView.as_view(), name='inscription_reminder'),
    path(r'tba/date.htm', views.pratique, name='pratique'),
    path(r'tba/', views.static_page, kwargs={'page' : 'index'}, name='static_index'),
    path(r'tba/<slug:page>.htm', views.static_page, name='static_pages'),
]
