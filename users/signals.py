from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from users.models import Bet, Schedule

User = get_user_model()

@receiver(post_save, sender=User)
def create_default_bets(sender, instance, created, **kwargs):
    if created:
        # Get all schedule matches
        schedule_matches = Schedule.objects.all()

        # Create default bets for each match with initial scores as '0'
        for match in schedule_matches:
            Bet.objects.create(user=instance, match=match, predicted_home_score=0, predicted_away_score=0)
