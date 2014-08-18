# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0006_auto_20140718_0516'),
    ]

    operations = [
        migrations.AddField(
            model_name='inscription',
            name='certificat',
            field=models.FileField(upload_to=b'', null=True, verbose_name=b'Certificat M\xc3\xa9dical', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='inscription',
            name='fiche_inscr',
            field=models.FileField(upload_to=b'', null=True, verbose_name=b"Fiche d'inscription", blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='inscription',
            name='fiche_sanit',
            field=models.FileField(upload_to=b'', null=True, verbose_name=b'Fiche sanitaire', blank=True),
            preserve_default=True,
        ),
    ]
