from django.contrib import admin
from .models import CustomUser, Match, Bet

class MatchAdmin(admin.ModelAdmin):
    list_filter = ('week_number',) 

class BetAdmin(admin.ModelAdmin):
    list_filter = ('match__week_number','user__username',)  


admin.site.register(CustomUser)
admin.site.register(Match, MatchAdmin)  
admin.site.register(Bet, BetAdmin)  
