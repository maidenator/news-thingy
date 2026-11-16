from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from news.models import UserSubscription

User = get_user_model()


class AuthenticationSliceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        self.logout_url = reverse('accounts:logout')
        self.home_url = reverse('core:home')
        self.user_data = {
            'username': 'newspioneer',
            'email': 'pioneer@newsthingy.com',
            'password': 'ComplexPassword123!',
        }

    def test_register_get_view(self):
        """GET /accounts/register/ loads successfully and has link back to login."""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
        self.assertContains(response, 'Create an Account')
        # Check transition link to Login screen
        self.assertContains(response, self.login_url)

    def test_register_post_success_and_direct_onboarding(self):
        """POST /accounts/register/ creates user, auto-authenticates, and transitions directly to home briefing."""
        post_data = {
            'username': self.user_data['username'],
            'email': self.user_data['email'],
            'password1': self.user_data['password'],
            'password2': self.user_data['password'],
        }
        response = self.client.post(self.register_url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        # Check direct transition to home briefing
        self.assertTemplateUsed(response, 'core/home.html')
        self.assertTrue(User.objects.filter(username='newspioneer').exists())
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertTrue(UserSubscription.objects.filter(user__username='newspioneer').exists())
        self.assertContains(response, "Welcome to News Thingy, newspioneer!")

    def test_register_post_mismatched_passwords(self):
        """Registration fails if passwords do not match."""
        post_data = {
            'username': 'mismatchuser',
            'email': 'mismatch@example.com',
            'password1': 'Password123!',
            'password2': 'DifferentPassword123!',
        }
        response = self.client.post(self.register_url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='mismatchuser').exists())
        self.assertFormError(response.context['form'], 'password2', "The two password fields didn’t match.")

    def test_login_get_view(self):
        """GET /accounts/login/ loads successfully and has transition link to register."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertContains(response, 'Log In')
        # Check transition link to Register screen
        self.assertContains(response, self.register_url)

    def test_login_post_success_and_transition_to_home(self):
        """Successful login transitions to home screen."""
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        login_data = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
        self.assertTrue(response.context['user'].is_authenticated)

    def test_login_post_invalid_credentials(self):
        """Invalid credentials stay on login screen and display error."""
        login_data = {
            'username': 'unknown_user',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertFalse(response.context['user'].is_authenticated)

    def test_authenticated_user_redirected_from_login_and_register(self):
        """Already logged in users are redirected to home if they visit login or register."""
        user = User.objects.create_user(
            username='activeuser',
            email='active@example.com',
            password='Password123!'
        )
        self.client.force_login(user)

        res_login = self.client.get(self.login_url)
        self.assertRedirects(res_login, self.home_url)

        res_reg = self.client.get(self.register_url)
        self.assertRedirects(res_reg, self.home_url)

    def test_logout_redirects_to_login(self):
        """Logging out terminates session and redirects back to login screen."""
        user = User.objects.create_user(
            username='logoutuser',
            email='logout@example.com',
            password='Password123!'
        )
        self.client.force_login(user)

        response = self.client.post(self.logout_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertContains(response, "successfully logged out")
