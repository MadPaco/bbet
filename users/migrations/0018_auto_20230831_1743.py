# Generated by Django 3.0.1 on 2023-08-31 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_auto_20230831_1404'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='odds_away',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='match',
            name='odds_home',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
