# Generated by Django 5.1 on 2024-09-11 06:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_alter_room_topic'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='topic',
        ),
    ]