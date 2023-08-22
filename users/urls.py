from django.urls import path
from .views import SignUpView, HomePageView, ScheduleView, PredictionsView, FellowBetsView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('schedule/', ScheduleView.as_view(), name='schedule'),
    path('predictions/', PredictionsView.as_view(), name='predictions'),
    path('fellow_bets/<int:week_number>/', FellowBetsView.as_view(), name='fellow_bets'),
]
