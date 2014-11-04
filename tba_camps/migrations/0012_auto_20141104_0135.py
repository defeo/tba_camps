# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0011_auto_20141102_2002'),
    ]

    operations = [
        migrations.AddField(
            model_name='inscription',
            name='licence',
            field=models.CharField(default='', max_length=31, verbose_name=b'Num\xc3\xa9ro de licence', blank=True),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='inscription',
            name='licencie',
        ),
    ]
