# Generated by Django 3.0.1 on 2023-08-23 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_delete_team'),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('name', models.CharField(blank=True, max_length=50, primary_key=True, serialize=False)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='team_logos/')),
            ],
        ),
    ]
