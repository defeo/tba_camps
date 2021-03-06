# Generated by Django 2.0 on 2018-01-10 22:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0039_auto_20180103_1302'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stagiaire',
            name='assurance',
        ),
        migrations.AddField(
            model_name='dossier',
            name='assurance',
            field=models.BooleanField(default=True, help_text='6€ par stagiaire', verbose_name='Assurance annulation'),
        ),
        migrations.AlterField(
            model_name='dossier',
            name='hebergement',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tba_camps.Hebergement'),
        ),
    ]
