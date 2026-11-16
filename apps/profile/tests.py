from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Profile


class ProfileFeatureTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('profile_reader', 'profile@example.com', 'Password123!')
        self.client.force_login(self.user)

    def test_profile_is_created_and_updated(self):
        response = self.client.post(reverse('profile:profile'), {'full_name': 'Profile Reader', 'bio': 'Enjoys concise reporting.'}, follow=True)
        self.assertEqual(response.status_code, 200)
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.full_name, 'Profile Reader')
        self.assertContains(response, 'Your profile has been updated.')
