# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0015_auto_20150218_0014'),
    ]

    operations = [
        migrations.AddField(
            model_name='inscription',
            name='motif',
            field=models.CharField(default=b'', max_length=255, verbose_name=b'Motif du suppl\xc3\xa9ment', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='inscription',
            name='supplement',
            field=models.DecimalField(default=0, verbose_name=b'Suppl\xc3\xa9ment', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
    ]
