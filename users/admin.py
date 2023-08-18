from django.contrib import admin
from .models import CustomUser, Match, Bet
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Match)
admin.site.register(Bet)
