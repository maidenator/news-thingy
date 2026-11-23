from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from news.models import Article, Category, Outlet, Summary
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

    def test_profile_displays_reading_stats(self):
        cat = Category.objects.create(name='Tech', slug='tech')
        outlet = Outlet.objects.create(name='Inq', slug='inq', category=cat, website_url='https://example.com')
        article = Article.objects.create(
            outlet=outlet,
            category=cat,
            title='Profile Stat Story',
            url='https://example.com/stat-story',
            published_at=timezone.now(),
            original_read_time_minutes=6,
        )
        Summary.objects.create(article=article, tldr='Short brief.', summary_read_time_seconds=60)
        article.read_by.add(self.user)
        article.bookmarked_by.add(self.user)

        response = self.client.get(reverse('profile:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['stats']['stories_read'], 1)
        self.assertEqual(response.context['stats']['minutes_saved'], 5)
        self.assertEqual(response.context['stats']['bookmarks'], 1)
        self.assertContains(response, 'Stories read')
        self.assertContains(response, '5 min')
