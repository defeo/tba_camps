# Generated by Django 2.0 on 2018-01-21 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0042_auto_20180115_0320'),
    ]

    operations = [
        migrations.AddField(
            model_name='stagiaire',
            name='acompte',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]