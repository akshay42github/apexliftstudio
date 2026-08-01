"""
Context processors for global template variables.
"""
from django.conf import settings


def site_settings(request):
    """Add site-wide settings to template context."""
    return {
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
        'site_name': 'ApexLiftStudio',
    }