from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class HomeViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.home_url = reverse('core:home')
        self.login_url = reverse('accounts:login')
        self.user = User.objects.create_user(
            username='readerone',
            email='reader@example.com',
            password='TestPassword123!'
        )

    def test_home_unauthenticated_redirects_to_login(self):
        """Unauthenticated user accessing home is redirected to the login screen."""
        response = self.client.get(self.home_url)
        expected_redirect = f"{self.login_url}?next={self.home_url}"
        self.assertRedirects(response, expected_redirect)

    def test_home_authenticated_renders_editorial_front_page(self):
        """Authenticated subscriber accessing home sees the front page briefing and dispatches."""
        self.client.force_login(self.user)
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
        self.assertContains(response, 'NEWS THINGY')
        self.assertContains(response, 'readerone')
        self.assertContains(response, 'Curated for readerone')
        # Editorial standards & AI transparency note in footer/headers
        self.assertContains(response, 'Editorial Standards')
        self.assertContains(response, 'LLM assistance')
