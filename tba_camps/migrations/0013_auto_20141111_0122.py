# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tba_camps.models


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0012_auto_20141104_0135'),
    ]

    operations = [
        migrations.AddField(
            model_name='hebergement',
            name='managed',
            field=models.BooleanField(default=False, verbose_name=b"Envoyer fiche d'inscription \xc3\xa0 TBA"),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='inscription',
            name='fiche_hotel',
            field=tba_camps.models.FileField(upload_to=b'', null=True, verbose_name=b'R\xc3\xa9servation h\xc3\xa9bergement', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='inscription',
            name='fiche_hotel_snail',
            field=models.BooleanField(default=False, verbose_name=b'R\xc3\xa9servation h\xc3\xa9bergement re\xc3\xa7ue'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='inscription',
            name='fiche_inscr_snail',
            field=models.BooleanField(default=False, verbose_name=b'Inscription envoy\xc3\xa9e re\xc3\xa7ue'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='inscription',
            name='fiche_sanit_snail',
            field=models.BooleanField(default=False, verbose_name=b'Fiche sanitaire envoy\xc3\xa9e re\xc3\xa7ue'),
            preserve_default=True,
        ),
    ]
