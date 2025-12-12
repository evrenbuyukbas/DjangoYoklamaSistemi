from django.urls import path
from . import views # Görünüm fonksiyonlarını (views.py) import eder.

urlpatterns = [
    # Ana dizin ('') artık dashboard'a eşittir (Yukarıdaki include sayesinde).
    path('', views.dashboard, name='dashboard'), 
    path('video_feed/', views.video_feed, name='video_feed'), 
    path('kayit_ekle/', views.kayit_ekle, name='kayit_ekle'), 
] 