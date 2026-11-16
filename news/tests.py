from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from news.models import Category, Outlet, Article, Summary, UserSubscription

User = get_user_model()


class NewsDomainAndFeedITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='reader_jane',
            email='jane@example.com',
            password='SecretPassword123!'
        )
        self.category_biz = Category.objects.create(name='Business & Economy', slug='business-economy')
        self.category_gov = Category.objects.create(name='Nation & Governance', slug='nation-governance')

        self.outlet_bw = Outlet.objects.create(
            name='BusinessWorld',
            slug='businessworld',
            category=self.category_biz,
            website_url='https://www.bworldonline.com',
            badge_label='BW'
        )
        self.outlet_inq = Outlet.objects.create(
            name='Philippine Daily Inquirer',
            slug='inquirer',
            category=self.category_gov,
            website_url='https://newsinfo.inquirer.net',
            badge_label='INQ'
        )

        self.article_bsp = Article.objects.create(
            outlet=self.outlet_bw,
            category=self.category_biz,
            title='BSP Cuts Benchmark Rate to 6.00%',
            url='https://bworldonline.com/bsp-cuts-rate',
            published_at=timezone.now(),
            original_read_time_minutes=8
        )
        self.summary_bsp = Summary.objects.create(
            article=self.article_bsp,
            tldr='BSP eases monetary stance as headline inflation cools.',
            key_takeaways=['Headline inflation decelerates', 'Stimulates consumer and retail financing'],
            summary_read_time_seconds=60,
            ai_model='Gemini 1.5 Flash'
        )

    def test_summary_minutes_saved_calculation(self):
        """Verify minutes saved property calculates accurately."""
        # 8 minutes original - 1 minute summary = 7 minutes saved
        self.assertEqual(self.summary_bsp.minutes_saved, 7)

    def test_front_page_shows_briefings_and_source_links(self):
        """Authenticated user sees editorial front page with source links and summaries."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')
        self.assertContains(response, 'BSP Cuts Benchmark Rate to 6.00%')
        self.assertContains(response, 'BSP eases monetary stance as headline')
        self.assertContains(response, 'Headline inflation decelerates')
        # Check source URL citation
        self.assertContains(response, 'https://bworldonline.com/bsp-cuts-rate')

    def test_category_filtering(self):
        """Filtering by category returns only stories within that category."""
        self.client.force_login(self.user)
        
        # Filter by business-economy (should contain article)
        res_biz = self.client.get(f"{reverse('core:home')}?category=business-economy")
        self.assertContains(res_biz, 'BSP Cuts Benchmark Rate to 6.00%')

        # Filter by nation-governance (no articles currently under nation & governance in this test)
        res_gov = self.client.get(f"{reverse('core:home')}?category=nation-governance")
        self.assertNotContains(res_gov, 'BSP Cuts Benchmark Rate to 6.00%')

    def test_toggle_outlet_subscription(self):
        """User can follow and unfollow outlets via toggle view."""
        self.client.force_login(self.user)
        toggle_url = reverse('core:toggle_subscription', args=[self.outlet_bw.id])

        # Initially not subscribed
        sub, _ = UserSubscription.objects.get_or_create(user=self.user)
        self.assertFalse(sub.outlets.filter(id=self.outlet_bw.id).exists())

        # Follow
        res = self.client.post(toggle_url, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(sub.outlets.filter(id=self.outlet_bw.id).exists())

        # Unfollow
        res = self.client.post(toggle_url, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(sub.outlets.filter(id=self.outlet_bw.id).exists())
