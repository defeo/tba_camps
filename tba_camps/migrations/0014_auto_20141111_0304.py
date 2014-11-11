# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tba_camps.models


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0013_auto_20141111_0122'),
    ]

    operations = [
        migrations.AddField(
            model_name='inscription',
            name='certificat_snail',
            field=models.BooleanField(default=False, verbose_name=b'Certificat m\xc3\xa9dical re\xc3\xa7u'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='inscription',
            name='certificat',
            field=tba_camps.models.FileField(upload_to=b'', null=True, verbose_name=b'Certificat m\xc3\xa9dical', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='inscription',
            name='fiche_inscr_snail',
            field=models.BooleanField(default=False, verbose_name=b"Fiche d'inscription re\xc3\xa7ue"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='inscription',
            name='fiche_sanit_snail',
            field=models.BooleanField(default=False, verbose_name=b'Fiche sanitaire re\xc3\xa7ue'),
            preserve_default=True,
        ),
    ]
