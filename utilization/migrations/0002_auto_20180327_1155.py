# Generated by Django 2.0.3 on 2018-03-27 18:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utilization', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='document',
            old_name='docfile',
            new_name='file',
        ),
    ]
