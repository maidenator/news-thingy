from django.urls import path

from . import views

app_name = 'insights'
urlpatterns = [
    path('articles/', views.article_index, name='article_index'),
    path('summaries/', views.summarized_articles, name='summarized_articles'),
]
