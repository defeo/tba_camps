# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0012_auto_20150202_1905'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inscription',
            name='assurance',
            field=models.DecimalField(default=Decimal('6.00'), max_digits=10, decimal_places=2, choices=[(Decimal('0.00'), b'Non'), (Decimal('6.00'), 'Avec assurance (6\u20ac)')]),
            preserve_default=True,
        ),
    ]
