from django.contrib import admin
from .models import CustomUser, Schedule, Bet
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Schedule)
admin.site.register(Bet)
