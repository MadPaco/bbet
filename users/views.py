from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, ListView
from django.db.models import Q
from .forms import CustomUserCreationForm
from .models import Schedule

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
        # Fetch the list of all unique team names from the database
        context['team_names'] = Schedule.objects.order_by().values_list('home_team', 'away_team').distinct()
        return context