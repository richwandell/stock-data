# Generated by Django 3.1.7 on 2021-03-28 20:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stonksconfig', '0003_datasourcecredentials'),
    ]

    operations = [
        migrations.RenameField(
            model_name='datasource',
            old_name='type',
            new_name='dstype',
        ),
    ]
