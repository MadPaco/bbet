from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Bet, Schedule
from django.forms import formset_factory, BaseModelFormSet

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email', 'age',)

class CustomUserChangeForm(UserChangeForm):
    
    class Meta(UserChangeForm):
        model = CustomUser
        fields = ('username', 'email', 'age',)

class PredictionForm(forms.ModelForm):
    class Meta:
        model = Bet
        fields = ['match', 'predicted_home_score', 'predicted_away_score']

class PredictionFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        selected_week = kwargs.pop('selected_week', 1)
        super().__init__(*args, **kwargs)
        if selected_week:
            self.queryset = Bet.objects.filter(match__week_number=selected_week)

        else:
            self.queryset = Bet.objects.filter(match__week_number=1)

PredictionFormSet = formset_factory(PredictionForm, formset=PredictionFormSet, extra=0)