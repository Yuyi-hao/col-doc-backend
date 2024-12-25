from django.urls import path
from . import views

urlpatterns = [
    path('notifications', views.notifications, name="notifications"),
    path('notifications/<int:notification_id>/mark/', views.mark_notification, name="mark-notification"),
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name="delete-notification"),
]