from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('write/', views.write, name='write'),
    path('detail/<int:post_id>/', views.detail, name='detail'),
    path('edit/<int:post_id>/', views.edit, name='edit'),  
    path('accounts/login/', auth_views.LoginView.as_view(template_name='user/login.html'), name='login'),
    path('signup/', views.signup, name='signup'),
    path('like/<int:post_id>/', views.toggle_like, name='toggle_like'),
]

