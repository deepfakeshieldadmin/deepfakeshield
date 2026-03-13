"""
Global context processors for templates.
"""


def global_context(request):
    """Add global variables to all templates."""
    return {
        'project_name': 'Deep Fake Shield',
        'project_version': '1.0.0',
        'project_tagline': 'Real-Time Media Authenticity Verification',
    }