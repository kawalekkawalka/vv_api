# Generated by Django 4.2.3 on 2023-07-10 20:22

import api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_player_image_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=api.models.upload_path_handler),
        ),
    ]
