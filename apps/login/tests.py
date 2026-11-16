from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class LoginFeatureTests(TestCase):
    def test_login_template_uses_feature_assets(self):
        response = self.client.get(reverse('login:login'))
        self.assertTemplateUsed(response, 'login/login.html')
        self.assertContains(response, 'css/login/login.css')
        self.assertContains(response, 'js/login/login.js')

    def test_login_redirects_to_feature_home(self):
        user = get_user_model().objects.create_user('feature_reader', 'feature@example.com', 'Password123!')
        response = self.client.post(reverse('login:login'), {'username': user.username, 'password': 'Password123!'})
        self.assertRedirects(response, reverse('home:home'))
