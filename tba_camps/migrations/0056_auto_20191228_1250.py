# Generated by Django 3.0.1 on 2019-12-28 11:50

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0055_reversible'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reversible',
            name='max_stature',
            field=models.IntegerField(null=True, validators=[django.core.validators.MaxValueValidator(300), django.core.validators.MinValueValidator(100)], verbose_name='Stature max (cm)'),
        ),
        migrations.AlterField(
            model_name='reversible',
            name='min_stature',
            field=models.IntegerField(null=True, validators=[django.core.validators.MaxValueValidator(300), django.core.validators.MinValueValidator(100)], verbose_name='Stature min (cm)'),
        ),
    ]
