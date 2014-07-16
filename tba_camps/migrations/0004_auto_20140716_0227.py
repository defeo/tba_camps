# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def order_model(model):
    def forwards(apps, se):
        Model = apps.get_model('tba_camps', model)
        db_alias = se.connection.alias
        for i, o in enumerate(Model.objects.all()):
            o.order = i
            o.save()
    return forwards

class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0003_auto_20140716_0136'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='formule',
            options={'ordering': (b'order',)},
        ),
        migrations.AlterModelOptions(
            name='hebergement',
            options={'ordering': (b'order',)},
        ),
        migrations.AddField(
            model_name='formule',
            name='order',
            field=models.PositiveIntegerField(default=0, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='hebergement',
            name='order',
            field=models.PositiveIntegerField(default=0, editable=False, db_index=True),
            preserve_default=False,
        ),
        migrations.RunPython(order_model('Hebergement'), lambda *x: None),
        migrations.RunPython(order_model('Formule'), lambda *x: None),
    ]
