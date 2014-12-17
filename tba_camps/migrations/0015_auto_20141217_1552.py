# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0014_auto_20141111_0304'),
    ]

    operations = [
        migrations.AddField(
            model_name='inscription',
            name='parrain',
            field=models.BooleanField(default=False, verbose_name=b'Parrain'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='inscription',
            name='train',
            field=models.IntegerField(default=0, verbose_name=b'Suppl\xc3\xa9ment aller-retour train depuis Paris', choices=[(0, b'Pas de suppl\xc3\xa9ment'), (160, b'Tarif normal (160\xe2\x82\xac)'), (80, b'Moins de 12 ans (80\xe2\x82\xac)')]),
            preserve_default=True,
        ),
    ]
