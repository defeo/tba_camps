# Generated by Django 2.0.1 on 2018-02-03 17:36

from django.db import migrations, models
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0043_stagiaire_acompte'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(db_index=True, editable=False)),
                ('message', tinymce.models.HTMLField()),
                ('etat', models.CharField(choices=[('0', 'Email non confirmée'), ('1', 'Pré-inscription incomplète'), ('P', 'Pré-inscription'), ('V', 'Validé'), ('C', 'Complet'), ('A', 'Annulé')], max_length=1, verbose_name='État du dossier')),
                ('formule', models.ManyToManyField(to='tba_camps.Formule')),
                ('hebergement', models.ManyToManyField(to='tba_camps.Hebergement')),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
    ]
