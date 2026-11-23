from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from news.models import Article, Category, Outlet, Summary


class HomeSearchAndFilterTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='reader_test',
            email='reader_test@example.com',
            password='TestPassword123!'
        )
        self.category_tech = Category.objects.create(name='Technology', slug='technology')
        self.category_biz = Category.objects.create(name='Business', slug='business')

        self.outlet_inq = Outlet.objects.create(
            name='Daily Inquirer',
            slug='daily-inquirer',
            category=self.category_tech,
            website_url='https://example.com/inq'
        )
        self.outlet_bworld = Outlet.objects.create(
            name='BusinessWorld',
            slug='business-world',
            category=self.category_biz,
            website_url='https://example.com/bworld'
        )

        self.article1 = Article.objects.create(
            outlet=self.outlet_inq,
            category=self.category_tech,
            title='AI Startup Secures Seed Funding in Manila',
            url='https://example.com/ai-startup',
            published_at=timezone.now()
        )
        Summary.objects.create(
            article=self.article1,
            tldr='A Manila-based artificial intelligence startup announced a fresh funding round.',
            key_takeaways=['Raised $2M in seed capital', 'Expanding research lab team']
        )

        self.article2 = Article.objects.create(
            outlet=self.outlet_bworld,
            category=self.category_biz,
            title='Central Bank Keeps Benchmark Rates Unchanged',
            url='https://example.com/central-bank-rates',
            published_at=timezone.now()
        )
        Summary.objects.create(
            article=self.article2,
            tldr='Monetary board opted to hold key interest rates steady amid moderating inflation.',
            key_takeaways=['Policy rate maintained', 'Inflation expectations remain anchored']
        )

    def test_unauthenticated_redirect(self):
        response = self.client.get(reverse('home:home'))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_view_renders_search_bar(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('home:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="q"')
        self.assertContains(response, 'AI Startup Secures Seed Funding in Manila')
        self.assertContains(response, 'Central Bank Keeps Benchmark Rates Unchanged')

    def test_home_includes_articles_without_summaries(self):
        Article.objects.create(
            outlet=self.outlet_inq,
            category=self.category_tech,
            title='Breaking Story Awaiting Summary',
            url='https://example.com/breaking-no-summary',
            published_at=timezone.now(),
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse('home:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Breaking Story Awaiting Summary')
        self.assertContains(response, 'Summary pending')

    def test_search_by_title_query(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('home:home'), {'q': 'Startup'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Startup Secures Seed Funding in Manila')
        self.assertNotContains(response, 'Central Bank Keeps Benchmark Rates Unchanged')

    def test_search_by_outlet_name(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('home:home'), {'q': 'BusinessWorld'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'AI Startup Secures Seed Funding in Manila')
        self.assertContains(response, 'Central Bank Keeps Benchmark Rates Unchanged')

    def test_search_and_category_combined(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('home:home'), {'category': 'technology', 'q': 'Startup'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Startup Secures Seed Funding in Manila')
        self.assertNotContains(response, 'Central Bank Keeps Benchmark Rates Unchanged')

    def test_toggle_bookmark_and_saved_stories_filter(self):
        self.client.force_login(self.user)
        # Initially not bookmarked
        self.assertFalse(self.article1.bookmarked_by.filter(id=self.user.id).exists())

        # Toggle bookmark on
        response = self.client.post(reverse('home:toggle_bookmark', args=[self.article1.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.article1.bookmarked_by.filter(id=self.user.id).exists())

        # Check saved filter view
        saved_view = self.client.get(reverse('home:home'), {'saved': '1'})
        self.assertEqual(saved_view.status_code, 200)
        self.assertContains(saved_view, 'AI Startup Secures Seed Funding in Manila')
        self.assertNotContains(saved_view, 'Central Bank Keeps Benchmark Rates Unchanged')

        # Toggle bookmark off
        response_off = self.client.post(reverse('home:toggle_bookmark', args=[self.article1.id]))
        self.assertEqual(response_off.status_code, 302)
        self.assertFalse(self.article1.bookmarked_by.filter(id=self.user.id).exists())

    def test_following_only_filter(self):
        self.client.force_login(self.user)
        # Before following any outlet, ?following=1 returns no stories
        empty_response = self.client.get(reverse('home:home'), {'following': '1'})
        self.assertEqual(empty_response.status_code, 200)
        self.assertNotContains(empty_response, 'AI Startup Secures Seed Funding in Manila')
        self.assertContains(empty_response, 'Following (0)')

        # Follow Daily Inquirer via toggle endpoint
        self.client.post(reverse('home:toggle_subscription', args=[self.outlet_inq.id]))
        filtered_response = self.client.get(reverse('home:home'), {'following': '1'})
        self.assertEqual(filtered_response.status_code, 200)
        self.assertContains(filtered_response, 'AI Startup Secures Seed Funding in Manila')
        self.assertNotContains(filtered_response, 'Central Bank Keeps Benchmark Rates Unchanged')
        self.assertContains(filtered_response, 'Following (1)')

