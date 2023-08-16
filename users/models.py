from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """ custom User class, adding an age field"""
    age = models.PositiveIntegerField(null=True, blank=True)


class Schedule(models.Model):
    match_number = models.PositiveIntegerField(primary_key=True)
    week_number = models.PositiveIntegerField()
    date = models.DateTimeField()
    location = models.CharField(max_length=100)
    home_team = models.CharField(max_length=50)
    away_team = models.CharField(max_length=50)
    result = models.CharField(max_length=20)

    def __str__(self):
        return f"Week {self.week_number}: {self.away_team} at {self.home_team}"


class Bet(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    match = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    predicted_home_score = models.PositiveIntegerField()
    predicted_away_score = models.PositiveIntegerField()
