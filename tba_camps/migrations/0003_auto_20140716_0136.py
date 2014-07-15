# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0002_auto_20140716_0001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inscription',
            name='assurance',
            field=models.IntegerField(default=0, choices=[(0, b'Non'), (6, 'Avec assurance (6\u20ac)')]),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='navette_a',
            field=models.IntegerField(default=0, verbose_name=b'Navette aller', choices=[(0, b'Non'), (6, 'Oui (6\u20ac)')]),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='navette_r',
            field=models.IntegerField(default=0, verbose_name=b'Navette retour', choices=[(0, b'Non'), (6, 'Oui (6\u20ac)')]),
        ),
    ]
