# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-02 22:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0022_auto_20160102_2344'),
    ]

    operations = [
        migrations.RenameField(
            model_name='formule',
            old_name='affiche_accompagneteur',
            new_name='affiche_accompagnateur',
        ),
    ]
