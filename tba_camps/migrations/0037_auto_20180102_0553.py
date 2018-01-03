# Generated by Django 2.0 on 2018-01-02 04:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0036_auto_20171231_1612'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='formule',
            name='hebergements',
        ),
        migrations.RemoveField(
            model_name='semaine',
            name='complet',
        ),
        migrations.RemoveField(
            model_name='stagiaire',
            name='hebergement',
        ),
        migrations.AddField(
            model_name='dossier',
            name='hebergement',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tba_camps.Hebergement'),
        ),
        migrations.AddField(
            model_name='formule',
            name='has_hebergement',
            field=models.BooleanField(default=False, verbose_name='Résa Hébergement'),
        ),
        migrations.AddField(
            model_name='semaine',
            name='formule_complet',
            field=models.ManyToManyField(to='tba_camps.Formule'),
        ),
        migrations.AddField(
            model_name='semaine',
            name='hbgt_complet',
            field=models.ManyToManyField(to='tba_camps.Hebergement'),
        ),
        migrations.AlterField(
            model_name='hebergement',
            name='managed',
            field=models.CharField(choices=[('M', 'Géré par TBA'), ('E', 'Réservé par le client')], default='M', max_length=1, verbose_name='Mode réservation'),
        ),
    ]