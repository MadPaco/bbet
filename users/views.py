from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, ListView, FormView
from django.db.models import Q
from .forms import CustomUserCreationForm, BetForm
from .models import Schedule, Bet

class HomePageView(TemplateView):
    template_name = 'home.html'

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

class ScheduleView(ListView):
    model = Schedule
    template_name = 'schedule.html'
    ordering = 'week_number'
    context_object_name = 'schedule_data'
    paginate_by = None

    def get_queryset(self):
        selected_team = self.request.GET.get('team')
        if selected_team:
            queryset = Schedule.objects.filter(Q(home_team=selected_team) | Q(away_team=selected_team))
        else:
            queryset = Schedule.objects.all()
        return queryset.order_by('week_number')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch the list of all unique home teams and away teams from the database separately
        home_teams = Schedule.objects.order_by().values_list('home_team', flat=True).distinct()
        away_teams = Schedule.objects.order_by().values_list('away_team', flat=True).distinct()

        # Combine the unique home teams and away teams and convert to a set to remove duplicates
        unique_teams = set(list(home_teams) + list(away_teams))

        # Convert the set back to a list and sort it alphabetically
        unique_teams_list = sorted(list(unique_teams))

        # Assign the sorted list to 'team_names' in the context
        context['team_names'] = unique_teams_list
        return context
    
class BetView(FormView):
    template_name = 'bet_form.html'
    form_class = BetForm
    success_url = reverse_lazy('schedule')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['match'] = Schedule.objects.get(pk=self.kwargs['pk'])
        return kwargs

    def form_valid(self, form):
        match = Schedule.objects.get(pk=self.kwargs['pk'])
        home_team_score = form.cleaned_data['home_team_score']
        away_team_score = form.cleaned_data['away_team_score']
        #points = calculate_points(match, home_team_score, away_team_score)

        bet = Bet(
            user=self.request.user,
            match=match,
            home_team_score=home_team_score,
            away_team_score=away_team_score,
            #points=points,
        )
        bet.save()
        return super().form_valid(form)

    #def calculate_points(self, match, home_team_score, away_team_score):
        # Implement your logic to calculate points based on predictions
        # You can compare the predicted scores with the actual scores
        # and assign points based on correctness.
        # For example, you can assign points for correct result (win/draw/loss),
        # partial points for correct tendency, and more.

        # Return the calculated points here
        #return calculated_points