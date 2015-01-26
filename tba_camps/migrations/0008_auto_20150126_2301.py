# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0007_auto_20150126_2236'),
    ]

    operations = [
        migrations.AddField(
            model_name='formule',
            name='affiche_mode',
            field=models.BooleanField(default=True, verbose_name=b'Option Mode de r\xc3\xa9gl\xc3\xa9ment'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='formule',
            name='affiche_assurance',
            field=models.BooleanField(default=True, verbose_name=b'Option Assurance'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='formule',
            name='affiche_chambre',
            field=models.BooleanField(default=False, verbose_name=b"Option 'En chambre avec'"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='formule',
            name='affiche_hebergement',
            field=models.BooleanField(default=False, verbose_name=b'Option H\xc3\xa9bergement'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='formule',
            name='affiche_navette',
            field=models.BooleanField(default=True, verbose_name=b'Option Navette'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='formule',
            name='affiche_train',
            field=models.BooleanField(default=False, verbose_name=b'Option Train'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='formule',
            name='publique',
            field=models.BooleanField(default=True, verbose_name=b'Tout publique'),
            preserve_default=True,
        ),
    ]
