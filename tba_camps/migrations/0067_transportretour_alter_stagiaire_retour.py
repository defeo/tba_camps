# Generated by Django 4.2.7 on 2023-12-08 22:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("tba_camps", "0066_remove_formule_affiche_navette_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="TransportRetour",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("tba_camps.transport",),
        ),
        migrations.AlterField(
            model_name="stagiaire",
            name="retour",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="retour",
                to="tba_camps.transportretour",
            ),
        ),
    ]
