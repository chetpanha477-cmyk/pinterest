from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('', views.home, name='landing'),
    path('explore/', views.explore, name='explore'),
    path('about/', views.about, name='about'),
    path('businesses/', views.businesses, name='businesses'),
    path('news/', views.news, name='news'),
    path('load-more/', views.load_more_pins, name='load_more_pins'),
    path('pin/new/', views.pin_create, name='pin_create'),
    path('pin/<int:pk>/', views.pin_detail, name='pin_detail'),
    path('pin/<int:pk>/delete/', views.pin_delete, name='pin_delete'),
    path('pin/<int:pk>/save/', views.pin_save_toggle, name='pin_save_toggle'),
    path('boards/', views.board_list, name='board_list'),
    path('boards/new/', views.board_create, name='board_create'),
    path('boards/<int:pk>/', views.board_detail, name='board_detail'),
    path('saved/', views.saved_pins, name='saved_pins'),
    path('u/<str:username>/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
