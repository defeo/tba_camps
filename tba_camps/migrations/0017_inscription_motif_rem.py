# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0016_auto_20150428_0238'),
    ]

    operations = [
        migrations.AddField(
            model_name='inscription',
            name='motif_rem',
            field=models.CharField(default=b'', max_length=255, verbose_name=b'Motif de la remise', blank=True),
            preserve_default=True,
        ),
    ]
