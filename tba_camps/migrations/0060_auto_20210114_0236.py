# Generated by Django 3.0.1 on 2021-01-14 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0059_auto_20200109_0025'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stagiaire',
            name='adr_parrain',
        ),
        migrations.AddField(
            model_name='stagiaire',
            name='noms_parraines',
            field=models.TextField(blank=True, verbose_name='NOMS Prénoms parrainés'),
        ),
    ]
