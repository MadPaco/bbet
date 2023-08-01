from django.urls import path
from .views import SignUpView, HomePageView, ScheduleView, BetView

urlpatterns = [
    path('', HomePageView.as_view(), name = 'home'),
    path('signup/', SignUpView.as_view(), name = 'signup'),
    path('schedule/', ScheduleView.as_view(), name = 'schedule'),
    path('bet/<int:pk>/', BetView.as_view(), name='bet_match'),
]