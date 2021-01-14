# Generated by Django 3.0.1 on 2019-12-19 22:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0052_auto_20190808_1429'),
    ]

    operations = [
        migrations.CreateModel(
            name='Backpack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prenom', models.CharField(blank=True, max_length=15, verbose_name='Prénom')),
                ('numero', models.CharField(blank=True, max_length=2, verbose_name='Numéro')),
                ('dossier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tba_camps.Dossier')),
            ],
        ),
    ]