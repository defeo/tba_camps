# Generated by Django 3.0.1 on 2019-12-28 12:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0057_auto_20191228_1251'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reversible',
            options={'ordering': ('min_stature',)},
        ),
        migrations.AddField(
            model_name='stagiaire',
            name='reversible',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='tba_camps.Reversible'),
        ),
    ]
