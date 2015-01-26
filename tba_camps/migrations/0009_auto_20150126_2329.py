# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0008_auto_20150126_2301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formule',
            name='affiche_assurance',
            field=models.BooleanField(default=True, verbose_name=b'Opt. assurance'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='formule',
            name='affiche_chambre',
            field=models.BooleanField(default=False, verbose_name=b"Opt. 'chambre avec'"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='formule',
            name='affiche_hebergement',
            field=models.BooleanField(default=False, verbose_name=b'Opt. h\xc3\xa9bergement'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='formule',
            name='affiche_mode',
            field=models.BooleanField(default=True, verbose_name=b'Opt. mode r\xc3\xa9gl\xc3\xa9ment'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='formule',
            name='affiche_navette',
            field=models.BooleanField(default=True, verbose_name=b'Opt. navette'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='formule',
            name='affiche_train',
            field=models.BooleanField(default=False, verbose_name=b'Opt. train'),
            preserve_default=True,
        ),
    ]
