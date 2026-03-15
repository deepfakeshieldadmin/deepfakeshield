"""
Global template context processors for DeepFake Shield.
"""
from django.conf import settings


def global_context(request):
    """Add global context variables to all templates."""
    return {
        'PROJECT_NAME': settings.DEEPFAKE_SHIELD['PROJECT_NAME'],
        'PROJECT_VERSION': settings.DEEPFAKE_SHIELD['PROJECT_VERSION'],
        'PROJECT_TAGLINE': settings.DEEPFAKE_SHIELD['PROJECT_TAGLINE'],
        'IS_DEBUG': settings.DEBUG,
    }