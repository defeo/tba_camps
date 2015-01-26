# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0009_auto_20150126_2329'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inscription',
            name='mode',
            field=models.CharField(default=b'', max_length=1023, verbose_name=b'Mode de r\xc3\xa8glement', blank=True),
            preserve_default=True,
        ),
    ]
