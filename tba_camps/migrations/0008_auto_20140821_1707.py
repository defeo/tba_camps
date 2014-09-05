# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import tba_camps.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tba_camps', '0007_auto_20140814_1727'),
    ]

    operations = [
        migrations.CreateModel(
            name='Manager',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('notif', models.BooleanField(default=True, verbose_name=b'Re\xc3\xa7oit un mail ')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='certificat',
            field=tba_camps.models.FileField(upload_to=b'', null=True, verbose_name=b'Certificat M\xc3\xa9dical', blank=True),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='fiche_inscr',
            field=tba_camps.models.FileField(upload_to=b'', null=True, verbose_name=b"Fiche d'inscription", blank=True),
        ),
        migrations.AlterField(
            model_name='inscription',
            name='fiche_sanit',
            field=tba_camps.models.FileField(upload_to=b'', null=True, verbose_name=b'Fiche sanitaire', blank=True),
        ),
    ]
