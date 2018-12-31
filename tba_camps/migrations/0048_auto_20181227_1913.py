# Generated by Django 2.1.3 on 2018-12-27 18:13

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0047_auto_20181227_1825'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dossier',
            name='assurance',
            field=models.DecimalField(choices=[(Decimal('0.00'), "Pas d'assurance"), (Decimal('6.00'), 'Assurance light'), (Decimal('30.00'), 'Assurancetourix')], decimal_places=2, default=Decimal('0.00'), max_digits=10, verbose_name='Assurance annulation'),
        ),
        migrations.AlterField(
            model_name='stagiaire',
            name='train',
            field=models.DecimalField(choices=[(Decimal('0.000'), 'Pas de supplément'), (Decimal('160.000'), 'Aller-retour tarif normal (160€)'), (Decimal('80.000'), 'Aller-retour moins de 12 ans (80€)'), (Decimal('80.001'), 'Aller tarif normal (80€)'), (Decimal('40.000'), 'Aller moins de 12 ans (40€)'), (Decimal('80.002'), 'Retour tarif normal (80€)'), (Decimal('40.001'), 'Retour moins de 12 ans (40€)')], decimal_places=3, default=Decimal('0.000'), max_digits=10, verbose_name='Supplément train depuis Paris'),
        ),
    ]
