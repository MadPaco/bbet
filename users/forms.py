from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Team
from django import forms


class CustomUserCreationForm(UserCreationForm):

    favorite_team = forms.ModelChoiceField(queryset=Team.objects.all(), required=True, widget=forms.Select())

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email', 'favorite_team',)


class CustomUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm):
        model = CustomUser
        fields = ('username', 'email', 'favorite_team',)
