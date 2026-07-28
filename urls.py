# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.game_home, name='game_home'),
    path('play/', views.play_action, name='play_action'),
]