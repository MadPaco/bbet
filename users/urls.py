from django.urls import path
from .views import SignUpView, HomePageView, ScheduleView

urlpatterns = [
    path('', HomePageView.as_view(), name = 'home'),
    path('signup/', SignUpView.as_view(), name = 'signup'),
    path('schedule/', ScheduleView.as_view(), name = 'schedule'),
]