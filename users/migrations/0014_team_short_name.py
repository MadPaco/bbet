# Generated by Django 3.0.1 on 2023-08-26 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_customuser_favorite_team'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='short_name',
            field=models.TextField(blank=True, null=True),
        ),
    ]