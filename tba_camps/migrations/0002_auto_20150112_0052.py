# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inscription',
            name='etat',
            field=models.CharField(default=b'V', max_length=1, verbose_name=b"\xc3\x89tat de l'inscription", choices=[(b'P', b'Pr\xc3\xa9-inscription'), (b'V', b'Valid\xc3\xa9'), (b'A', b'Annul\xc3\xa9')]),
            preserve_default=True,
        ),
    ]
