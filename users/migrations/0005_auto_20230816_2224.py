# Generated by Django 3.0.1 on 2023-08-16 20:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20230808_1552'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Schedule',
            new_name='Match',
        ),
    ]
