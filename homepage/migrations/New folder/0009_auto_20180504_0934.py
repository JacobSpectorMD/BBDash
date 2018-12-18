# Generated by Django 2.0.3 on 2018-05-04 16:34

from django.db import migrations, models
import django.db.models.deletion
import homepage.models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0008_auto_20180504_0928'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transfusion',
            name='user',
        ),
        migrations.AddField(
            model_name='transfusion',
            name='profile',
            field=models.ForeignKey(default=homepage.models.Profile, on_delete=django.db.models.deletion.CASCADE, to='homepage.Profile'),
        ),
    ]
