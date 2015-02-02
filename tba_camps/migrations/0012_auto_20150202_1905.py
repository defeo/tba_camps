# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0011_auto_20150202_1859'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inscription',
            name='taille',
            field=models.IntegerField(blank=True, null=True, verbose_name=b'Taille (cm)', validators=[django.core.validators.MaxValueValidator(300), django.core.validators.MinValueValidator(30)]),
            preserve_default=True,
        ),
    ]
