# -*- encoding: utf-8 

from django.core import mail
from django.conf import settings
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse

def get_managers():
    'Liste des administrateurs qui recoivent les notifications'
    from models import Manager
    return [m.user.email for m in Manager.objects.filter(notif=True)]

def send_mail(subject, recipients, template, obj, ctx=None):
    "Fonction d'utilite pour envoyer des mails"
    ctx = ctx or {}
    ctx.update(obj=obj,settings=settings)
    return mail.send_mail(
        subject=subject,
        from_email=settings.FROM_EMAIL,
        recipient_list=recipients,
        message=render_to_string('mails/%s.txt' % template, ctx),
        html_message=render_to_string('mails/%s.html' % template, ctx),
    )

# Actions utilisateur
def preinscr(obj):
    'Pre-inscription initiale'
    obj.send_mail()
    admin_url = settings.HOST + reverse('admin:tba_camps_inscription_change', args=(obj.id,))
    send_mail(
        subject="Nouvelle demande d'inscription",
        recipients=get_managers(),
        template='preinscr_admin',
        obj=obj,
        ctx={ 'admin_url': admin_url }
    )

def inscr_modif(obj):
    'Telechargement de pieces jointes'
    admin_url = settings.HOST + reverse('admin:tba_camps_inscription_change', args=(obj.id,))
    send_mail(
        subject="Nouvelle pièce jointe",
        recipients=get_managers(),
        template='inscr_modif',
        obj=obj,
        ctx={ 'admin_url': admin_url }
    )
