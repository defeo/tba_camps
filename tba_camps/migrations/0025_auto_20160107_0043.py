# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-06 23:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0024_inscription_date_valid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inscription',
            name='date_valid',
            field=models.DateField(blank=True, null=True, verbose_name=b'Date validation'),
        ),
    ]
