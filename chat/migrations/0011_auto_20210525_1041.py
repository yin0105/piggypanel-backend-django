# Generated by Django 3.1 on 2021-05-25 07:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0010_auto_20210525_1037'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='groupmessagepermission',
            options={'ordering': ['sender_group']},
        ),
    ]