from django.urls import reverse_lazy
from django.forms import formset_factory
from django.views.generic import CreateView, TemplateView, ListView, FormView, View
from django.db.models import Q
from .forms import CustomUserCreationForm, PredictionForm, PredictionFormSet
from .models import Schedule, Bet
from django.shortcuts import render

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
        selected_week = self.request.GET.get('week')
        queryset = Schedule.objects.all()

        if selected_team:
            queryset = queryset.filter(Q(home_team=selected_team) | Q(away_team=selected_team))
        if selected_week:
            queryset = queryset.filter(week_number=selected_week)
        return queryset.order_by('week_number')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #first, create a list of all the unique team names
        home_teams = Schedule.objects.order_by().values_list('home_team', flat=True).distinct()
        away_teams = Schedule.objects.order_by().values_list('away_team', flat=True).distinct()
        unique_teams = set(list(home_teams) + list(away_teams))
        unique_teams_list = sorted(list(unique_teams))
        context['team_names'] = unique_teams_list
        context['selected_team'] = self.request.GET.get('team')
        context['weeks'] = Schedule.objects.values_list('week_number', flat=True).distinct()

        return context
    
class PredictionsView(View):
    template_name = 'predictions.html'

    def get(self, request, *args, **kwargs):
        selected_week = self.request.GET.get('week_number', 1)
        if selected_week:
            games = Bet.objects.filter(user=request.user, match__week_number=selected_week)
        else:
            games = Bet.objects.filter(user=request.user, match__week_number=1)

        context = {
            'selected_week': selected_week,
            'games': games,
        }

        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        formset = self.formset_class(request.POST)
        
        if formset.is_valid():
            selected_week = self.request.POST.get('week_number')
            for form in formset:
                if form.cleaned_data.get('match') and form.cleaned_data.get('predicted_home_score') and form.cleaned_data.get('predicted_away_score'):
                    match = form.cleaned_data['match']
                    Bet.objects.create(
                        user=request.user,
                        match=match,
                        predicted_home_score=form.cleaned_data['predicted_home_score'],
                        predicted_away_score=form.cleaned_data['predicted_away_score']
                    )
            
            return redirect('predictions')
        
        weeks = Schedule.objects.values_list('week_number', flat=True).distinct()
        schedule = Schedule.objects.filter(week_number=selected_week)
        context = {
            'weeks': weeks,
            'selected_week': selected_week,
            'schedule': schedule,
            'formset': formset,
        }
        
        return render(request, self.template_name, context)