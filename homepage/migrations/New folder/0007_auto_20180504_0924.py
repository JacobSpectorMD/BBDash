# Generated by Django 2.0.3 on 2018-05-04 16:24

from django.db import migrations, models
import django.db.models.deletion
import homepage.models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0006_auto_20180504_0917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transfusion',
            name='profile',
            field=models.ForeignKey(default=homepage.models.Profile, on_delete=django.db.models.deletion.CASCADE, to='homepage.Profile'),
        ),
    ]
