# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-03 00:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0028_auto_20161201_0026'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='formule',
            name='affiche_hebergement',
        ),
        migrations.AddField(
            model_name='formule',
            name='hebergements',
            field=models.ManyToManyField(to='tba_camps.Hebergement'),
        ),
        migrations.AddField(
            model_name='semaine',
            name='complet',
            field=models.ManyToManyField(to='tba_camps.Hebergement'),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='formule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tba_camps.Formule'),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='hebergement',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tba_camps.Hebergement'),
        ),
    ]
