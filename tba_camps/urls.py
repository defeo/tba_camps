from django.urls import include, path
from django.views.generic import RedirectView, TemplateView
from . import views, models, sms, ffbb_api,admin

urlpatterns = [
    path(r'', RedirectView.as_view(url='/tba/', permanent=True)),
    path(r'index-tba.htm', RedirectView.as_view(url='/tba/presentation.htm', permanent=True)),
    path(r'admin/', admin.site.urls),
    path(r'sms/', include(sms.urls)),
    path(r'tba/inscriptions.htm', views.RegisterView.as_view(), name='register_form'),
    path(r'tba/dossier/', include([
        path('', views.DossierView.as_view(), name='dossier_view'),
        path('modify/', views.DossierModify.as_view(), name='dossier_modify'),
        path('<int:pk>;<slug:secret>/', views.dossier_redirect, name='dossier_redirect'),
        path('logout', views.dossier_logout, name='dossier_logout'),
        path('stagiaire/', views.StagiaireCreate.as_view(), name='stagiaire_create'),
        path('stagiaire/<int:pk>', views.StagiaireModify.as_view(), name='stagiaire_modify'),
        path('stagiaire/<int:pk>/delete', views.StagiaireDelete.as_view(), name='stagiaire_delete'),
    ])),
    # path(r'tba/inscriptions.htm/<slug:slug>/', include([
    #     path(r'', views.InscriptionView.as_view(), name='inscription_view'),
    #     path(r'fiche/', views.InscriptionPDFView.as_view(), name='inscription_pdf_view'),
    # ] + models.urls)),
    path(r'tba/date.htm', views.pratique, name='pratique'),
    path(r'tba/', views.static_page, kwargs={'page' : 'index'}, name='static_index'),
    path(r'tba/<slug:page>.htm', views.static_page, name='static_pages'),
]
