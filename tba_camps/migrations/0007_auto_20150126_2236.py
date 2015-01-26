# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0006_formule_publique'),
    ]

    operations = [
        migrations.AddField(
            model_name='formule',
            name='affiche_assurance',
            field=models.BooleanField(default=True, verbose_name=b'Afficher option Assurance'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='formule',
            name='affiche_navette',
            field=models.BooleanField(default=True, verbose_name=b'Afficher option Navette'),
            preserve_default=True,
        ),
    ]
