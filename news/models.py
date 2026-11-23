from django.db import models
from django.conf import settings


class Category(models.Model):
    """Topic category for news organization (e.g., Technology, World News)."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Outlet(models.Model):
    """News publication or outlet (e.g., Reuters, The Verge, BBC)."""
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='outlets')
    website_url = models.URLField()
    rss_feed_url = models.URLField(blank=True)
    badge_label = models.CharField(max_length=20, default="NEWS")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Article(models.Model):
    """Individual news article indexed from an outlet."""
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE, related_name='articles')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='articles')
    title = models.CharField(max_length=300)
    url = models.URLField(unique=True, verbose_name="Original Article URL")
    author = models.CharField(max_length=150, blank=True, default="Editorial Desk")
    published_at = models.DateTimeField()
    original_read_time_minutes = models.PositiveIntegerField(default=5)
    bookmarked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='bookmarked_articles'
    )
    read_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='read_articles'
    )

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class Summary(models.Model):
    """AI-generated concise summary and key takeaways for an article."""
    article = models.OneToOneField(Article, on_delete=models.CASCADE, related_name='summary')
    tldr = models.TextField(help_text="Executive summary of 2-3 sentences.")
    key_takeaways = models.JSONField(
        default=list,
        help_text="List of bullet points highlighting essential developments."
    )
    summary_read_time_seconds = models.PositiveIntegerField(
        default=45,
        help_text="Time in seconds needed to read the summary."
    )
    ai_model = models.CharField(max_length=50, default="Gemini 1.5 Flash")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Summaries"

    def __str__(self):
        return f"Summary: {self.article.title}"

    @property
    def minutes_saved(self):
        original = self.article.original_read_time_minutes
        summary_min = max(1, round(self.summary_read_time_seconds / 60))
        return max(1, original - summary_min)


class UserSubscription(models.Model):
    """User-specific subscription to outlets and categories."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    outlets = models.ManyToManyField(Outlet, blank=True, related_name='subscribers')
    categories = models.ManyToManyField(Category, blank=True, related_name='subscribers')
    daily_digest_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Subscription preferences for {self.user.username}"
