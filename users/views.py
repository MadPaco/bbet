from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, TemplateView, ListView, View
from django.db.models import Q
from .forms import CustomUserCreationForm
from .models import Match, Bet, CustomUser
from django.shortcuts import render
from django.contrib.auth.mixins import UserPassesTestMixin


class HomePageView(TemplateView):
    template_name = 'home.html'


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


class ScheduleView(ListView):
    model = Match
    template_name = 'schedule.html'
    ordering = 'week_number'
    context_object_name = 'schedule_data'
    paginate_by = None

    def get_queryset(self):
        selected_team = self.request.GET.get('team')
        selected_week = self.request.GET.get('week')
        queryset = Match.objects.all()

        if selected_team:
            queryset = queryset.filter(Q(home_team=selected_team) | Q(away_team=selected_team))
        if selected_week:
            queryset = queryset.filter(week_number=selected_week)
        return queryset.order_by('week_number')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # first, create a list of all the unique team names
        home_teams = Match.objects.order_by().values_list('home_team', flat=True).distinct()
        away_teams = Match.objects.order_by().values_list('away_team', flat=True).distinct()
        unique_teams = set(list(home_teams) + list(away_teams))
        unique_teams_list = sorted(list(unique_teams))
        context['team_names'] = unique_teams_list
        context['selected_team'] = self.request.GET.get('team')
        context['weeks'] = Match.objects.values_list('week_number', flat=True).distinct()

        return context


class PredictionsView(View):
    template_name = 'predictions.html'

    def get(self, request, *args, **kwargs):
        
        selected_week = request.COOKIES.get('selectedWeekPredictions', 1)
        games = Bet.objects.filter(user=request.user, match__week_number=selected_week)
        weeks = Match.objects.values_list('week_number', flat=True).distinct()
        context = {
            'selected_week': selected_week,
            'games': games,
            'weeks': weeks,
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        selected_week = request.COOKIES['selectedWeekPredictions']
        print(selected_week)
        games = Bet.objects.filter(user=request.user, match__week_number=selected_week)
        weeks = Match.objects.values_list('week_number', flat=True).distinct()

        for game in games:
            home_score_key = f"predicted_home_score_{game.match.pk}"
            away_score_key = f"predicted_away_score_{game.match.pk}"
            predicted_home_score = request.POST.get(home_score_key)
            predicted_away_score = request.POST.get(away_score_key)

            if predicted_home_score is not None and predicted_away_score is not None:
                game.predicted_home_score = int(predicted_home_score)
                game.predicted_away_score = int(predicted_away_score)
                game.save()

        context = {
            'selected_week': selected_week,
            'games': games,
            'weeks': weeks,
        }

        return render(request, self.template_name, context)

class EnterResultsView(UserPassesTestMixin, ListView):
    model = Match
    template_name = 'enter_results.html'
    context_object_name = 'matches'

    def get_queryset(self):
        week_number = self.kwargs.get('week_number')
        return Match.objects.filter(week_number=week_number)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['weeks'] = range(1, 19)
        return context

    def test_func(self):
        return self.request.user.is_staff  # Only allow staff users to enter results
    
    def get_success_url(self):
        week_number = self.kwargs.get('week_number')
        return reverse('enter_results', kwargs={'week_number': week_number})
    
class FellowBetsView(ListView):
    model = Bet
    template_name = 'fellow_bets.html'
    context_object_name = 'bets'

    def get_queryset(self):
        week_number = self.kwargs.get('week_number')
        return Bet.objects.filter(match__week_number=week_number)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['weeks'] = range(1, 19)
        context['matches'] = Match.objects.filter(week_number=self.kwargs.get('week_number'))
        context['users'] = CustomUser.objects.all()
        context['week_number'] = self.kwargs.get('week_number')
        
        return context
    