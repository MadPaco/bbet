from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, ListView

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