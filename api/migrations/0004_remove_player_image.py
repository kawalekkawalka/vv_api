# Generated by Django 4.2.3 on 2023-07-10 20:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_player_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='image',
        ),
    ]
