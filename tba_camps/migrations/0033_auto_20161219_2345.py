# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-19 22:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0032_auto_20161214_0208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formule',
            name='hebergements',
            field=models.ManyToManyField(blank=True, to='tba_camps.Hebergement'),
        ),
    ]
