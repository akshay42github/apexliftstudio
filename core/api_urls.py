"""
API URL patterns for ApexLiftStudio.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'plans', api_views.MembershipPlanViewSet, basename='api-plans')
router.register(r'locations', api_views.LocationViewSet, basename='api-locations')
router.register(r'classes', api_views.ClassViewSet, basename='api-classes')

urlpatterns = [
    path('', include(router.urls)),
    path('signup/', api_views.signup_view, name='api-signup'),
    path('login/', api_views.login_view, name='api-login'),
    path('user/profile/', api_views.user_profile_view, name='api-user-profile'),
    path('stripe/create-checkout/', api_views.create_checkout_session, name='api-create-checkout'),
    path('webhook/stripe/', api_views.stripe_webhook, name='api-stripe-webhook'),
]