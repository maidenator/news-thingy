from django.contrib import admin
from .models import Category, Outlet, Article, Summary, UserSubscription


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Outlet)
class OutletAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'badge_label', 'website_url')
    list_filter = ('category',)
    prepopulated_fields = {'slug': ('name',)}


class SummaryInline(admin.StackedInline):
    model = Summary
    can_delete = False


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'outlet', 'category', 'published_at')
    list_filter = ('outlet', 'category', 'published_at')
    search_fields = ('title', 'author')
    inlines = [SummaryInline]


@admin.register(Summary)
class SummaryAdmin(admin.ModelAdmin):
    list_display = ('article', 'ai_model', 'summary_read_time_seconds', 'created_at')


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'daily_digest_enabled', 'created_at')
    filter_horizontal = ('outlets', 'categories')
