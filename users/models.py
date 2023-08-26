from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class CustomUser(AbstractUser):
    """ custom User class, adding an age field"""
    age = models.PositiveIntegerField(null=True, blank=True)
    favorite_team = models.CharField(max_length=50, null=True, blank=True)
    

    def __str__(self):
        return self.username

class Team(models.Model):
    name = models.CharField(max_length=50, blank=True, primary_key=True)
    logo = models.ImageField(upload_to='team_logos/', null=True, blank=True)

    def __str__(self):
        return self.name

class Match(models.Model):
    match_number = models.PositiveIntegerField(primary_key=True)
    week_number = models.PositiveIntegerField()
    date = models.DateTimeField()
    location = models.CharField(max_length=100)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_team')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_team')
    home_team_result = models.IntegerField(null=True, blank=True)
    away_team_result = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Week {self.week_number}: {self.away_team} at {self.home_team}"


class Bet(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    predicted_home_score = models.PositiveIntegerField()
    predicted_away_score = models.PositiveIntegerField()
    points = models.IntegerField(default=0)
    
    def get_admin_url(self):
        return reverse("admin:%s_%s_change" % (self._meta.app_label, self._meta.model_name), args=(self.id,))

    def __str__(self):
        return f"{self.user.username} bet {self.predicted_home_score} - {self.predicted_away_score} on {self.match}"