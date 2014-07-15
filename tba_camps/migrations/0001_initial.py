# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import markupfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Formule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('prix', models.IntegerField()),
                ('taxe', models.IntegerField(default=0, verbose_name=b'Taxe menage')),
                ('cotisation', models.IntegerField(default=15, verbose_name=b'Cotisation TBA')),
                ('affiche_train', models.BooleanField(default=False, verbose_name=b"Afficher option Train \xc3\xa0 l'inscription")),
                ('affiche_hebergement', models.BooleanField(default=False, verbose_name=b"Afficher option H\xc3\xa9bergement \xc3\xa0 l'inscription")),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Hebergement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom', models.CharField(max_length=255)),
                ('commentaire', markupfield.fields.MarkupField(verbose_name=b"Commentaire affich\xc3\xa9 \xc3\xa0 l'inscription", blank=True)),
                ('commentaire_markup_type', models.CharField(default=b'markdown', max_length=30, blank=True, choices=[(b'', b'--'), (b'html', b'html'), (b'plain', b'plain'), (b'markdown', b'markdown')])),
                ('_commentaire_rendered', models.TextField(editable=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Inscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom', models.CharField(max_length=255)),
                ('prenom', models.CharField(max_length=255)),
                ('sexe', models.CharField(default=0, max_length=1, choices=[(b'H', b'Homme'), (b'F', b'Femme')])),
                ('naissance', models.DateField(verbose_name=b'Date de naissance')),
                ('lieu', models.CharField(max_length=255, verbose_name=b'Lieu de naissance')),
                ('adresse', models.TextField()),
                ('cp', models.CharField(max_length=10, verbose_name=b'Code postal')),
                ('ville', models.CharField(max_length=255)),
                ('pays', models.CharField(default=b'France', max_length=255)),
                ('email', models.EmailField(max_length=255, verbose_name=b'Adresse email', blank=True)),
                ('tel', models.CharField(max_length=20, verbose_name=b'T\xc3\xa9l\xc3\xa9phone', validators=[django.core.validators.RegexValidator(regex=b'^\\+?\\d{10,}$', message=b'Num\xc3\xa9ro invalide')])),
                ('train', models.IntegerField(default=0, verbose_name=b'Suppl\xc3\xa9ment aller-retour train depuis Paris', choices=[(0, b'Pas de suppl\xc3\xa9ment'), (150, b'Tarif normal (150\xe2\x82\xac)'), (75, b'Moins de 12 ans (75\xe2\x82\xac)')])),
                ('assurance', models.IntegerField(default=0, choices=[(0, b'Sans assurance'), (6, 'Avec assurance (6\u20ac)')])),
                ('mode', models.CharField(blank=True, max_length=2, verbose_name=b'Mode de r\xc3\xa8glement', choices=[(b'C', b'Ch\xc3\xa8que'), (b'E', b'Esp\xc3\xa8ces'), (b'VB', b'Virement bancaire'), (b'CV', b'Ch\xc3\xa8ques vacances'), (b'BC', b'Bons CAF')])),
                ('etat', models.CharField(default=b'V', max_length=1, verbose_name=b"\xc3\x89tat de l'inscription", choices=[(b'P', b'Pr\xc3\xa9-inscription'), (b'V', b'Valid\xc3\xa9'), (b'A', b'Annul\xc3\xa9'), (b'I', b'Mail non valide')])),
                ('licencie', models.CharField(default=0, max_length=1, verbose_name=b'Licenci\xc3\xa9 dans un club', choices=[(b'O', b'Oui'), (b'N', b'Non')])),
                ('venu', models.CharField(default=0, max_length=1, verbose_name=b'Je suis d\xc3\xa9j\xc3\xa0 venu \xc3\xa0 Superd\xc3\xa9voluy', choices=[(b'O', b'Oui'), (b'N', b'Non')])),
                ('taille', models.IntegerField(verbose_name=b'Taille (cm)', validators=[django.core.validators.MaxValueValidator(300), django.core.validators.MinValueValidator(30)])),
                ('nom_parrain', models.CharField(max_length=255, verbose_name=b'NOM Pr\xc3\xa9nom parrain', blank=True)),
                ('adr_parrain', models.CharField(max_length=255, verbose_name=b'Adresse parrain', blank=True)),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name=b'Date inscription')),
                ('slug', models.SlugField(max_length=22, editable=False, blank=True)),
                ('formule', models.ForeignKey(to='tba_camps.Formule')),
                ('hebergement', models.ForeignKey(blank=True, to='tba_camps.Hebergement', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Semaine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('debut', models.DateField(unique=True, verbose_name=b'D\xc3\xa9but de la semaine')),
                ('commentaire', models.CharField(max_length=255, verbose_name=b'Commentaire affich\xc3\xa9', blank=True)),
                ('places', models.IntegerField(default=0, verbose_name=b'Nombre de places')),
                ('fermer', models.BooleanField(default=False, verbose_name=b'Inscriptions ferm\xc3\xa9es')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='inscription',
            name='semaines',
            field=models.ManyToManyField(to='tba_camps.Semaine'),
            preserve_default=True,
        ),
    ]
