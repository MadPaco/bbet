import datetime
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, TemplateView, ListView, View, DetailView, UpdateView, DeleteView
from django.db.models import Q, Sum, Count
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import Match, Bet, CustomUser, Achievement, UserAchievement
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.utils import timezone
from django.contrib.auth import logout
from django.contrib import messages  
from .models import Bet, Match
from datetime import date, timedelta




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
            game.match.timestamp = int(game.match.date.timestamp())
            home_score_key = f"predicted_home_score_{game.match.pk}"
            away_score_key = f"predicted_away_score_{game.match.pk}"
            predicted_home_score = request.POST.get(home_score_key)
            predicted_away_score = request.POST.get(away_score_key)
            old_home_score = game.predicted_home_score
            old_away_score = game.predicted_away_score
            game.timestamp = current_time

            if predicted_home_score is not None and predicted_away_score is not None:
                if old_home_score != int(predicted_home_score) or old_away_score != int(predicted_away_score):
                    game.changes_count += 1

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
    
    def award_achievement(self, user, achievement_name):
        achievement = Achievement.objects.get(name=achievement_name)
        if not UserAchievement.objects.filter(user=user, achievement=achievement).exists():
            UserAchievement.objects.create(user=user, achievement=achievement, date_achieved=timezone.now())
    
        
    def post(self, request, *args, **kwargs):
        week_number = self.kwargs.get('week_number')
        matches = Match.objects.filter(week_number=week_number)
        users = CustomUser.objects.all()

        # Define the target timestamp
        target_timestamp = datetime.datetime(2023, 9, 1)  # This sets the time to 00:00:00 of September 1, 2023

        # Iterate over the Bet objects with a null timestamp and update them
        for bet in Bet.objects.filter(timestamp__isnull=True):
            bet.timestamp = target_timestamp
            bet.save()

        for match in matches:
            home_score_key = f"home_team_result_{match.match_number}"
            away_score_key = f"away_team_result_{match.match_number}"
            home_score = request.POST.get(home_score_key, 0)
            away_score = request.POST.get(away_score_key, 0)

            if home_score and away_score:
                match.home_team_result = int(home_score)
                match.away_team_result = int(away_score)
                match.save()

                bets = Bet.objects.filter(match=match)
                for bet in bets:
                    points = 0
                    if bet.predicted_home_score == match.home_team_result and bet.predicted_away_score == match.away_team_result:
                        points = 5
                        self.award_achievement(bet.user, "Detective")
                    elif (bet.predicted_home_score - bet.predicted_away_score) == (match.home_team_result - match.away_team_result):
                        points = 3
                    elif (bet.predicted_home_score > bet.predicted_away_score and match.home_team_result > match.away_team_result) or \
                        (bet.predicted_home_score < bet.predicted_away_score and match.home_team_result < match.away_team_result):
                        points = 1
                    bet.points = points
                    bet.save()
                

                    # Check for achievements:
                    # "Beginner's Luck"
                    if Bet.objects.filter(user=bet.user, points__gt=0).count() == 1:
                        self.award_achievement(bet.user, "Beginner's Luck")

                    if Bet.objects.filter(user=bet.user, changes_count__gt=5):
                        self.award_achievement(bet.user, "Second Thoughts")
                    # "Underdog"
                    if match.odds_home < 0 and bet.predicted_home_score > bet.predicted_away_score:
                        self.award_achievement(bet.user, "Underdog")
                    if match.odds_away < 0 and bet.predicted_away_score > bet.predicted_home_score:
                        self.award_achievement(bet.user, "Underdog")

                    # "Truther" 
                    if bet.user.favorite_team == match.home_team and match.odds_home < 0:
                        self.award_achievement(bet.user, "Truther")
                    if bet.user.favorite_team == match.away_team and match.odds_away < 0:
                        self.award_achievement(bet.user, "Truther")

                    # "Brave Soul"
                    if match.odds_home < 0 and bet.predicted_home_score - bet.predicted_away_score >= 10 and match.home_team_result - match.away_team_result >= 10:
                        self.award_achievement(bet.user, "Brave Soul")
                    if match.odds_away < 0 and bet.predicted_away_score - bet.predicted_home_score >= 10 and match.away_team_result - match.home_team_result >= 10:
                        self.award_achievement(bet.user, "Brave Soul")

                    # "last minute luck"
                    if bet.timestamp:
                        time_difference = match.date - bet.timestamp  # Assuming match.start_time is a DateTime field.
                        if time_difference.total_seconds() <= 60:  # 1 minute = 60 seconds
                            if bet.points > 0: 
                                self.award_achievement(bet.user, "Last Minute Luck")
                    else:
                        pass


        # Checks outside the match loop, that concern user's overall performance:
        # Note: These checks might need optimization for performance reasons.

        # "lucky number seven"
        for user in users:
            print(user)
            total_week_points = Bet.objects.filter(user=user, match__week_number=week_number).aggregate(week_points=Sum('points'))['week_points'] or 0
            if total_week_points >= 7:
                self.award_achievement(user, "Lucky Seven")

        # "Perfection"
        users_with_all_correct_bets = CustomUser.objects.annotate(correct_bets=Count('bet', filter=Q(bet__points__gt=0))).filter(correct_bets=matches.count())
        for user in users_with_all_correct_bets:
            self.award_achievement(user, "Perfection")

        # "Jackpot"
        users_with_77_points = CustomUser.objects.annotate(total_points=Sum('bet__points')).filter(total_points=77)
        for user in users_with_77_points:
            self.award_achievement(user, "Jackpot")


        # 'employee of the week for all users who share the highest score of the week'
        users_with_weekly_points = CustomUser.objects.annotate(
        week_points=Sum('bet__points', filter=Q(bet__match__week_number=week_number))
        ).order_by('-week_points')
        if not users_with_weekly_points.exists():
            return
        top_score = users_with_weekly_points.first().week_points
        top_scorers = users_with_weekly_points.filter(week_points=top_score)
        for scorer in top_scorers:
            self.award_achievement(scorer, "Employee of the week")

        #seasoned pro, expert and did you even try? all use bets placed, so we group this

        total_predictions = Bet.objects.filter(
            request.user,
            Q(predicted_home_score__gt=0) | Q(predicted_away_score__gt=0)
        ).count()
        if total_predictions >= 50:
            self.award_achievement(request.user, "Seasoned Pro")
        if total_predictions >= 100:
            self.award_achievement(request.user, "Expert")
        if total_predictions == 0:
            self.award_achievement(request.user, "Did You Even Try?")

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
        points_dict = {entry['points']: entry['count'] for entry in points_breakdown}
        context["points_1_count"] = points_dict.get(1, 0)
        context["points_3_count"] = points_dict.get(3, 0)
        context["points_5_count"] = points_dict.get(5, 0)    
        upcoming_matches = Match.objects.filter(Q(home_team=user.favorite_team) | Q(away_team=user.favorite_team),date__gt=timezone.now()).order_by('date')[:3]
        context['upcoming_matches'] = upcoming_matches

        user_achievements = UserAchievement.objects.filter(user=self.get_object())
        context['user_achievements'] = user_achievements

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
        return reverse_lazy('profile', kwargs={'username': self.request.user.username})

    def get_object(self, queryset=None):
        """Override to get the user based on the URL parameter"""
        username = self.kwargs.get('username')
        return get_object_or_404(CustomUser, username=username)

    def test_func(self):
        """Ensure the user is editing their own profile"""
        user_to_edit = self.get_object()
        return user_to_edit == self.request.user
    
class ProfileDeleteView(UserPassesTestMixin, DeleteView):
    model = CustomUser
    template_name = 'profile_confirm_delete.html'
    slug_field = 'username'  # specifying the field on the model that the slug represents
    slug_url_kwarg = 'username'  # the name of the keyword argument in the URL pattern
    success_url = reverse_lazy('home')

    def test_func(self):
        # Ensuring that the user trying to delete is the logged-in user
        return self.request.user == self.get_object()

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Profile deleted successfully!")
        logout(request)
        return super(ProfileDeleteView, self).delete(request, *args, **kwargs)


class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_current_nfl_week(self):
        today = datetime.date.today()
        start_date = datetime.date(2023, 9, 5)  

        # Check if today's date is before the NFL season starts
        if today < start_date:
            return "NFL season hasn't started yet."

        # Calculate the difference in days between today and the start date
        delta_days = (today - start_date).days

        # Calculate the NFL week
        week_number = delta_days // 7 + 1

        if week_number > 18:  # Assuming an 18 week season
            return "NFL regular season is over."

        return week_number

    def has_user_placed_bets_for_all_matches_this_week(self, user, current_week):
        total_matches_this_week = Match.objects.filter(week_number=current_week).count()

        # Filter bets where neither home_team_score nor away_team_score is 0
        user_bets_this_week = Bet.objects.filter(
            user=user, 
            match__week_number=current_week,
            predicted_home_score__gt=0, 
            predicted_away_score__gt=0
        ).count()
        
        return total_matches_this_week == user_bets_this_week
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['total_points'] = Bet.objects.filter(user=self.request.user).aggregate(total=Sum('points'))['total'] or 0

        # Fetch recent bets by the logged-in user
        context['recent_bets'] = Bet.objects.filter(user=self.request.user).order_by('match__date')[:5]

        current_week = self.get_current_nfl_week()
        context['has_placed_bets_for_all_matches'] = self.has_user_placed_bets_for_all_matches_this_week(self.request.user, current_week)
        
        # Fetch upcoming matches
        context['upcoming_matches'] = Match.objects.filter(date__gte=date.today()).order_by('date')[:5]
        
        ranked_users = CustomUser.objects.annotate(total_points=Sum('bet__points')).order_by('-total_points')
        user_rank = 1
        for rank, user in enumerate(ranked_users, start=1):
            if user == self.request.user:
                context['user_rank'] = rank
                break

        best_week_data = Bet.objects.filter(user=self.request.user).values('match__week_number').annotate(week_points=Sum('points')).order_by('-week_points').first()
        if best_week_data:
            context['best_week'] = {
                'number': best_week_data['match__week_number'],
                'points': best_week_data['week_points']
            }
        else:
            context['best_week'] = {
                'number': None,
                'points': None
            }

        # Fetch the latest achievement
        latest_achievement = UserAchievement.objects.filter(user=self.request.user).order_by('-date_achieved').first()
        context['latest_achievement'] = latest_achievement
            
        return context
    
