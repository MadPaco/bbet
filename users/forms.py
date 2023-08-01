from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser, Bet

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email', 'age',)

class CustomUserChangeForm(UserChangeForm):
    
    class Meta(UserChangeForm):
        model = CustomUser
        fields = ('username', 'email', 'age',)

class BetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Retrieve the user and match from the keyword arguments
        user = kwargs.pop('user', None)
        match = kwargs.pop('match', None)
        super().__init__(*args, **kwargs)
        
        # Set the user and match for the form instance
        self.user = user
        self.match = match

    class Meta:
        model = Bet
        fields = ['home_team_score', 'away_team_score']