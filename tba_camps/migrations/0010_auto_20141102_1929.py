# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0009_auto_20140905_0258'),
    ]

    operations = [
        migrations.AddField(
            model_name='inscription',
            name='notes',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='inscription',
            name='mode',
            field=models.CharField(max_length=1023, verbose_name=b'Mode de r\xc3\xa8glement', blank=True),
        ),
    ]
