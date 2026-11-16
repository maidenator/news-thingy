from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('outlets/<int:outlet_id>/toggle/', views.toggle_subscription_view, name='toggle_subscription'),
]
