# Generated by Django 3.0.1 on 2021-06-23 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0062_auto_20210201_2200'),
    ]

    operations = [
        migrations.AddField(
            model_name='stagiaire',
            name='arrivee',
            field=models.TimeField(blank=True, null=True, verbose_name='Horaire arrivée'),
        ),
    ]
