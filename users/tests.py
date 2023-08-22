from django.test import TestCase, Client
from django.urls import reverse
from users.models import CustomUser, Match, Bet
from users.views import HomePageView, SignUpView, ScheduleView, PredictionsView

class HomePageViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.home_url = reverse('home')

    def test_home_GET(self):
        response = self.client.get(self.home_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

class SignUpViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('signup')

    def test_signup_GET(self):
        response = self.client.get(self.signup_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')

    def test_signup_POST(self):
        response = self.client.post(self.signup_url, data={
            'username': 'testuser',
            'password1': 'testpassword',
            'password2': 'testpassword'
        })

        self.assertEquals(response.status_code, 302)  # Redirect after successful signup

class ScheduleViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.schedule_url = reverse('schedule')

    def test_schedule_GET(self):
        response = self.client.get(self.schedule_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'schedule.html')

class PredictionsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.predictions_url = reverse('predictions')

    def test_predictions_GET(self):
        response = self.client.get(self.predictions_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'predictions.html')