"""
Email utilities for DeepFake Shield.
Shows real errors instead of failing silently.
"""
import logging
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

logger = logging.getLogger(__name__)


def send_verification_email(user, token, request):
    """Send email verification link. Returns (success, error_message)."""
    verify_url = ''
    try:
        scheme = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        verify_url = f"{scheme}://{host}/verify-email/{token.token}/"

        context = {
            'user': user,
            'verify_url': verify_url,
            'project_name': 'DeepFake Shield',
        }

        html_message = render_to_string('emails/verify_email.html', context)
        plain_message = strip_tags(html_message)

        subject = 'Verify your email - DeepFake Shield'

        # Log what we're about to do
        logger.info(f"Sending verification email to: {user.email}")
        logger.info(f"Using backend: {settings.EMAIL_BACKEND}")
        logger.info(f"SMTP Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        logger.info(f"From: {settings.DEFAULT_FROM_EMAIL}")
        logger.info(f"Verify URL: {verify_url}")

        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.content_subtype = 'html'
        email.send(fail_silently=False)

        logger.info(f"✅ Email sent successfully to {user.email}")
        return True, None

    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ EMAIL FAILED: {error_msg}")
        logger.error(f"   Backend: {settings.EMAIL_BACKEND}")
        logger.error(f"   Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        logger.error(f"   User: {settings.EMAIL_HOST_USER}")
        logger.error(f"   TLS: {settings.EMAIL_USE_TLS}")
        logger.error(f"   Verify URL: {verify_url}")
        return False, error_msg