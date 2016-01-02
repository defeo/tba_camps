# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-02 22:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0021_inscription_mode_solde'),
    ]

    operations = [
        migrations.AddField(
            model_name='formule',
            name='affiche_accompagneteur',
            field=models.BooleanField(default=False, verbose_name=b'Opt. accompagnateur'),
        ),
        migrations.AddField(
            model_name='inscription',
            name='accompagnateur',
            field=models.CharField(blank=True, max_length=255, verbose_name=b"Nom de l'accompagnateur"),
        ),
    ]