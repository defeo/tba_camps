# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0015_auto_20141217_1552'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hebergement',
            name='_commentaire_rendered',
        ),
        migrations.RemoveField(
            model_name='hebergement',
            name='commentaire_markup_type',
        ),
        migrations.AlterField(
            model_name='hebergement',
            name='commentaire',
            field=models.TextField(verbose_name=b"Commentaire affich\xc3\xa9 \xc3\xa0 l'inscription", blank=True),
            preserve_default=True,
        ),
    ]
