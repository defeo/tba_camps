# Generated by Django 2.1.3 on 2019-01-05 22:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tba_camps', '0049_auto_20181231_1942'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='semaine',
            options={'ordering': ('debut',)},
        ),
    ]
