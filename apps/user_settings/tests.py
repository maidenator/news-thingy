from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import UserSettings


class SettingsFeatureTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('settings_reader', 'settings@example.com', 'Password123!')
        self.client.force_login(self.user)

    def test_settings_are_created_and_updated(self):
        response = self.client.post(reverse('user_settings:settings'), {'dark_mode': '', 'email_notifications': 'on'}, follow=True)
        self.assertEqual(response.status_code, 200)
        saved = UserSettings.objects.get(user=self.user)
        self.assertFalse(saved.dark_mode)
        self.assertTrue(saved.email_notifications)
        self.assertContains(response, 'preferences have been saved')
