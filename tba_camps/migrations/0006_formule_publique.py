# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0005_auto_20150126_1410'),
    ]

    operations = [
        migrations.AddField(
            model_name='formule',
            name='publique',
            field=models.BooleanField(default=True, verbose_name=b'Formule tout publique'),
            preserve_default=True,
        ),
    ]
