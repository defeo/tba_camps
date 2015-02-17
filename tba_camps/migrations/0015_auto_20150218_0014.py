# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0014_auto_20150217_0315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inscription',
            name='train',
            field=models.DecimalField(default=Decimal('0.00'), verbose_name=b'Suppl\xc3\xa9ment aller-retour train depuis Paris (inclut les navettes aller et retour)', max_digits=10, decimal_places=2, choices=[(Decimal('0.00'), b'Pas de suppl\xc3\xa9ment'), (Decimal('160.00'), b'Tarif normal (160\xe2\x82\xac)'), (Decimal('80.00'), b'Moins de 12 ans (80\xe2\x82\xac)')]),
            preserve_default=True,
        ),
    ]
