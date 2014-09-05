# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0008_auto_20140821_1707'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manager',
            name='notif',
            field=models.BooleanField(default=True, verbose_name=b'Re\xc3\xa7oit une notification \xc3\xa0 chaque action des utilisateurs'),
        ),
    ]
