# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0004_auto_20140716_0227'),
    ]

    operations = [
        migrations.AddField(
            model_name='formule',
            name='groupe',
            field=models.CharField(default=b'', max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='inscription',
            name='acompte',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='inscription',
            name='etat',
            field=models.CharField(default=b'V', max_length=1, verbose_name=b"\xc3\x89tat de l'inscription", choices=[(b'P', b'Pr\xc3\xa9-inscription'), (b'V', b'Valid\xc3\xa9'), (b'P', b'Pay\xc3\xa9'), (b'A', b'Annul\xc3\xa9')]),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='tel',
            field=models.CharField(max_length=20, verbose_name=b'T\xc3\xa9l\xc3\xa9phone', validators=[django.core.validators.RegexValidator(regex=b'^\\+?[\\d -\\.]{10,}$', message=b'Num\xc3\xa9ro invalide')]),
        ),
    ]
