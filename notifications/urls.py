from django.urls import path
from . import views

urlpatterns = [
    path('notifications', views.notifications),
    path('notifications/counts', views.notifications_counts),
    path('notifications/<int:notification_id>', views.particular_notification),
]