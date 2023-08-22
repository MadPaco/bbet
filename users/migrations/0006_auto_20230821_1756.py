# Generated by Django 3.0.1 on 2023-08-21 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20230816_2224'),
    ]

    operations = [
        migrations.AddField(
            model_name='bet',
            name='points',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='match',
            name='away_team_result',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='match',
            name='home_team_result',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]