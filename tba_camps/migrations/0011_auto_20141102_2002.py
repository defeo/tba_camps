# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0010_auto_20141102_1929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inscription',
            name='notes',
            field=models.TextField(default=b'', blank=True),
        ),
    ]
