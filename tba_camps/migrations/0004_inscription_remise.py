# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0003_inscription_prix_hebergement'),
    ]

    operations = [
        migrations.AddField(
            model_name='inscription',
            name='remise',
            field=models.IntegerField(default=0, verbose_name=b'Remise'),
            preserve_default=True,
        ),
    ]
