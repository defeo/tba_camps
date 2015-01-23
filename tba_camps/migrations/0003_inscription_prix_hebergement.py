# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0002_auto_20150112_0052'),
    ]

    operations = [
        migrations.AddField(
            model_name='inscription',
            name='prix_hebergement',
            field=models.IntegerField(default=0, verbose_name=b'Prix h\xc3\xa9bergement'),
            preserve_default=True,
        ),
    ]
