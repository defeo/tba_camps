# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='formule',
            name='affiche_chambre',
            field=models.BooleanField(default=False, verbose_name=b"Afficher option 'En chambre avec'"),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='inscription',
            name='chambre',
            field=models.CharField(default=b'', max_length=255, verbose_name=b'En chambre avec', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='inscription',
            name='navette_a',
            field=models.IntegerField(default=0, verbose_name=b'Navette aller', choices=[(0, b'Pas de navette'), (6, b'Navette (6\xe2\x82\xac)')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='inscription',
            name='navette_r',
            field=models.IntegerField(default=0, verbose_name=b'Navette retour', choices=[(0, b'Pas de navette'), (6, b'Navette (6\xe2\x82\xac)')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='formule',
            name='affiche_hebergement',
            field=models.BooleanField(default=False, verbose_name=b'Afficher option H\xc3\xa9bergement'),
        ),
        migrations.AlterField(
            model_name='formule',
            name='affiche_train',
            field=models.BooleanField(default=False, verbose_name=b'Afficher option Train'),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='email',
            field=models.EmailField(max_length=255, verbose_name=b'Adresse email (des parents)', blank=True),
        ),
    ]
