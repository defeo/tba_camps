# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-06 23:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0023_auto_20160102_2345'),
    ]

    operations = [
        migrations.AddField(
            model_name='inscription',
            name='date_valid',
            field=models.DateTimeField(null=True, verbose_name=b'Date validation'),
        ),
    ]