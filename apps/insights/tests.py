from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from news.models import Article, Category, Outlet, Summary


class InsightsQueryTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='insights_reader',
            email='insights_reader@example.com',
            password='TestPassword123!',
        )
        self.category = Category.objects.create(name='Fintech', slug='fintech')
        self.outlet = Outlet.objects.create(
            name='Manila Tech Wire',
            slug='manila-tech-wire',
            category=self.category,
            website_url='https://example.com/manila-tech-wire',
            badge_label='MTW',
        )
        self.summarized_article = Article.objects.create(
            outlet=self.outlet,
            category=self.category,
            title='Summarized Story About Digital Payments',
            url='https://example.com/summarized-story',
            published_at=timezone.now(),
        )
        Summary.objects.create(
            article=self.summarized_article,
            tldr='A concise summary of the digital payments story.',
            key_takeaways=['QR payments expanded'],
        )
        self.pending_article = Article.objects.create(
            outlet=self.outlet,
            category=self.category,
            title='Pending Story Without a Summary',
            url='https://example.com/pending-story',
            published_at=timezone.now(),
        )

    def test_article_index_requires_login(self):
        response = self.client.get(reverse('insights:article_index'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login:login'), response.url)

    def test_summarized_articles_requires_login(self):
        response = self.client.get(reverse('insights:summarized_articles'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login:login'), response.url)

    def test_article_index_shows_joined_outlet_and_category(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('insights:article_index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Summarized Story About Digital Payments')
        self.assertContains(response, 'Pending Story Without a Summary')
        self.assertContains(response, 'Manila Tech Wire')
        self.assertContains(response, 'Fintech')
        self.assertContains(response, 'Show generated SQL')

    def test_article_index_sql_contains_join(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('insights:article_index'), {'sql': '1'})
        sql = response.context['generated_sql']
        self.assertIn('JOIN', sql.upper())
        self.assertIn('news_outlet', sql)
        self.assertIn('news_category', sql)
        self.assertContains(response, 'Hide generated SQL')

    def test_summarized_articles_excludes_articles_without_summary(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('insights:summarized_articles'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Summarized Story About Digital Payments')
        self.assertNotContains(response, 'Pending Story Without a Summary')
        self.assertContains(response, 'Show generated SQL')

    def test_summarized_articles_sql_contains_subquery(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('insights:summarized_articles'), {'sql': '1'})
        sql = response.context['generated_sql']
        self.assertIn('IN (SELECT', sql.upper())
        self.assertIn('news_summary', sql)
        self.assertContains(response, 'Hide generated SQL')

    def test_outlet_breakdown_requires_login(self):
        response = self.client.get(reverse('insights:outlet_breakdown'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login:login'), response.url)

    def test_outlet_breakdown_aggregates_counts_and_sql(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('insights:outlet_breakdown'), {'sql': '1'})
        self.assertEqual(response.status_code, 200)
        outlet_row = response.context['outlets'][0]
        self.assertEqual(outlet_row.article_count, 2)
        self.assertEqual(outlet_row.summary_count, 1)
        sql = response.context['generated_sql'].upper()
        self.assertIn('COUNT(', sql)
        self.assertIn('AVG(', sql)
        self.assertIn('GROUP BY', sql)
        self.assertContains(response, 'Manila Tech Wire')
        self.assertContains(response, 'Hide generated SQL')
