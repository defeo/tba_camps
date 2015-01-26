# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0004_inscription_remise'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formule',
            name='cotisation',
            field=models.DecimalField(default=15, verbose_name=b'Cotisation TBA', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='formule',
            name='prix',
            field=models.DecimalField(max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='formule',
            name='taxe',
            field=models.DecimalField(default=0, verbose_name=b'Taxe menage', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='inscription',
            name='acompte',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='inscription',
            name='assurance',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2, choices=[(0, b'Non'), (6, 'Avec assurance (6\u20ac)')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='inscription',
            name='navette_a',
            field=models.DecimalField(default=0, verbose_name=b'Navette aller', max_digits=10, decimal_places=2, choices=[(0, b'Non'), (6, 'Oui (6\u20ac)')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='inscription',
            name='navette_r',
            field=models.DecimalField(default=0, verbose_name=b'Navette retour', max_digits=10, decimal_places=2, choices=[(0, b'Non'), (6, 'Oui (6\u20ac)')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='inscription',
            name='prix_hebergement',
            field=models.DecimalField(default=0, verbose_name=b'Prix h\xc3\xa9bergement', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='inscription',
            name='remise',
            field=models.DecimalField(default=0, verbose_name=b'Remise', max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='inscription',
            name='train',
            field=models.DecimalField(default=0, verbose_name=b'Suppl\xc3\xa9ment aller-retour train depuis Paris', max_digits=10, decimal_places=2, choices=[(0, b'Pas de suppl\xc3\xa9ment'), (160, b'Tarif normal (160\xe2\x82\xac)'), (80, b'Moins de 12 ans (80\xe2\x82\xac)')]),
            preserve_default=True,
        ),
    ]
