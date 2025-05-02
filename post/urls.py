from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('write/', views.write, name='write'),
    path('detail/<int:post_id>/', views.detail, name='detail'),
    path('edit/<int:post_id>/', views.edit, name='edit'),  # ← 수정 추가
    path('accounts/', include('django.contrib.auth.urls')),
]

