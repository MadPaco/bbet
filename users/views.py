from datetime import timedelta
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, TemplateView, ListView, View, DetailView, UpdateView
from django.db.models import Q, Sum, Count
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import Match, Bet, CustomUser
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.utils import timezone


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
            'current_time': timezone.now(),
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        try: 
            selected_week = request.COOKIES['selectedWeekPredictions']
        except KeyError:
            selected_week = 1

        games = Bet.objects.filter(user=request.user, match__week_number=selected_week)
        weeks = Match.objects.values_list('week_number', flat=True).distinct()
        current_time = timezone.now()

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
            'current_time': current_time,
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
    
        
    def post(self, request, *args, **kwargs):
        week_number = self.kwargs.get('week_number')
        matches = Match.objects.filter(week_number=week_number)

        for match in matches:
            home_score_key = f"home_team_result_{match.match_number}"
            away_score_key = f"away_team_result_{match.match_number}"

            try:
                home_score = request.POST.get(home_score_key)
            except ValueError:
                home_score = None
            try:
                away_score = request.POST.get(away_score_key)
            except ValueError:
                away_score = None
            print(type(home_score))
            if home_score is not None and len(home_score) > 0 and away_score is not None and len(away_score) > 0:
                match.home_team_result = int(home_score)
                match.away_team_result = int(away_score)
                match.save()

                bets = Bet.objects.filter(match=match)
                for bet in bets:
                    points = 0
                    if bet.predicted_home_score == match.home_team_result and bet.predicted_away_score == match.away_team_result:
                        points = 5
                    elif (bet.predicted_home_score - bet.predicted_away_score) == (match.home_team_result - match.away_team_result):
                        points = 3
                    elif (bet.predicted_home_score > bet.predicted_away_score and match.home_team_result > match.away_team_result) or \
                         (bet.predicted_home_score < bet.predicted_away_score and match.home_team_result < match.away_team_result):
                        points = 1
                    bet.points = points
                    bet.save()

        return redirect(self.get_success_url())
    
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
        context['current_time']: timezone.now()
        
        return context
    
class StandingsView(ListView):
    model = Bet
    template_name = 'standings.html'
    context_object_name = 'users'

    def get_queryset(self):
        return CustomUser.objects.all()

    def get_context_data(self, **kwargs):
        weeks = range(1, 19)
        context = super().get_context_data(**kwargs)
        context['weeks'] = weeks
        users = CustomUser.objects.all()
        context['users'] = users

        standings = {}
        grandTotal = {}

        for user in users:
            points = {}
            for week in weeks:
                weeklyPoints = 0
                weeklyBets = Bet.objects.filter(match__week_number=week, user=user)
                for bet in weeklyBets:
                    weeklyPoints += bet.points
                points[week] = weeklyPoints
            standings[user] = points
            grandTotal = {user.username: sum(points.values()) for user, points in standings.items()}

        context['standings'] = standings
        context['grandTotal'] = grandTotal

        return context

class ProfileView(DetailView):
    model = CustomUser
    template_name = 'profile.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context["weekly_points"] = Bet.objects.filter(user=user).values('match__week_number').annotate(week_points=Sum('points')).order_by('match__week_number')
        total_points_aggregate = Bet.objects.filter(user=user).aggregate(total_points=Sum('points'))
        context["total_points"] = total_points_aggregate['total_points'] or 0

        points_breakdown = Bet.objects.filter(user=user).values('points').annotate(count=Count('points'))
        context["points_breakdown"] = {entry['points']: entry['count'] for entry in points_breakdown}
        context["bio"] = user.bio
        return context
    
    def get_object(self):
        return get_object_or_404(CustomUser, username=self.kwargs['username'])

class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'profile_edit.html'  # Change to your template name
    
    def get_success_url(self):
        # After successfully editing the profile, redirect to the user's profile page.
        # This assumes you have a profile detail view that is accessible via 'profile_detail'
        # and accepts the user's ID as a parameter. Adjust as needed.
        return reverse_lazy('edit_profile', kwargs={'username': self.request.user.username})

    def test_func(self):
        # Ensure the user is editing their own profile
        return self.get_object() == self.request.user

    def get_object(self, queryset=None):
        # Get the current user object for editing
        return self.request.user