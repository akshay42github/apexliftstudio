"""
URL patterns for template views.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('plans/', views.plans_view, name='plans'),
    path('about/', views.about_view, name='about'),
    path('locations/', views.locations_view, name='locations'),
    path('classes/', views.classes_view, name='classes'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('contact/', views.contact_view, name='contact'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Auth URLs
    path('auth/login/', views.login_view, name='login'),
    path('auth/register/', views.register_view, name='register'),
    path('auth/logout/', views.logout_view, name='logout'),
]