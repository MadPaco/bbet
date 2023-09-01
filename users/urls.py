from django.urls import path
from .views import SignUpView, HomePageView, ScheduleView, PredictionsView, FellowBetsView, StandingsView, EnterResultsView, ProfileView, ProfileUpdateView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('schedule/', ScheduleView.as_view(), name='schedule'),
    path('predictions/', PredictionsView.as_view(), name='predictions'),
    path('fellow_bets/<int:week_number>/', FellowBetsView.as_view(), name='fellow_bets'),
    path('standings/', StandingsView.as_view(), name='standings'),
    path('enter_results/<int:week_number>/', EnterResultsView.as_view(), name='enter_results'),
    path('profile/<slug:username>/', ProfileView.as_view(), name='profile'),
    path('profile/<slug:username>/edit/', ProfileUpdateView.as_view(), name='edit_profile'),
]
