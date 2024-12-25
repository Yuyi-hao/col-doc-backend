from django.urls import path
from . import views

urlpatterns = [
    path('me', views.profile_user , name='user-profile'),
    path('register/', views.register_user , name='user-register'),
    path('login/', views.login_user , name='user-login'),
    path('logout/', views.logout_user , name='user-logout'),
    path('password-change/', views.change_password_user , name='user-password-change'),
    path('password-reset-request/', views.send_password_reset_email_user , name='user-password-reset-request'),
    path('reset-password/<uid>/<token>/', views.password_reset_user , name='user-password-reset'),
    path('token/refresh/', views.access_from_refresh, name='refresh-access-token')
]
