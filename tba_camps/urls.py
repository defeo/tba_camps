from django.urls import include, path
from django.views.generic import RedirectView, TemplateView
from . import views, sms, admin

urlpatterns = [
    path('', RedirectView.as_view(url='/tba/', permanent=True)),
    path('index-tba.htm', RedirectView.as_view(url='/tba/presentation.htm', permanent=True)),
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),
    path('sms/', include(sms.urls)),
    path('tba/inscriptions.htm', views.RegisterView.as_view(), name='register_form'),
    path('tba/dossier/', include([
        path('', views.DossierView.as_view(), name='dossier_view'),
        path('modify/', views.DossierModify.as_view(), name='dossier_modify'),
        path('confirm/', views.DossierConfirm.as_view(), name='dossier_confirm'),
        path('<int:pk>;<slug:secret>/', views.dossier_redirect, name='dossier_redirect'),
        path('logout', views.dossier_logout, name='dossier_logout'),
        path('stagiaire/', views.StagiaireCreate.as_view(), name='stagiaire_create'),
        path('stagiaire/<int:pk>/', include([
            path('', views.StagiaireModify.as_view(), name='stagiaire_modify'),
            path('delete', views.StagiaireDelete.as_view(), name='stagiaire_delete'),
            path('pdf', views.StagiairePDFView.as_view(), name='stagiaire_pdf_view'),
            path('uploads/', include([
                path('', views.StagiaireUpload.as_view(), name='stagiaire_upload'),
            ] + views.stagiaire_up_urls)),
        ])),
        *views.BackpackFact.urls,
        *views.TowelFact.urls,
        path('hebergement/', views.HebergementView.as_view(), name='hebergement_edit'),
    ])),
    path('tba/date.htm', views.pratique, name='pratique'),
    path('tba/', views.static_page, kwargs={'page' : 'index'}, name='static_index'),
    path('tba/<slug:page>.htm', views.static_page, name='static_pages'),
    path('tba/protected/<path>', views.Protected.as_view(), name='protected'),
]
