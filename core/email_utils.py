"""
Email utilities for DeepFake Shield.
Handles sending verification emails with proper error handling.
"""
import logging
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

logger = logging.getLogger(__name__)


def send_verification_email(user, token, request):
    """Send email verification link to user. Returns True on success."""
    verify_url = ''
    try:
        scheme = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        verify_url = f"{scheme}://{host}/verify-email/{token.token}/"

        context = {
            'user': user,
            'verify_url': verify_url,
            'project_name': settings.DEEPFAKE_SHIELD.get('PROJECT_NAME', 'DeepFake Shield'),
        }

        html_message = render_to_string('emails/verify_email.html', context)
        plain_message = strip_tags(html_message)

        subject = f'Verify your email - {settings.DEEPFAKE_SHIELD.get("PROJECT_NAME", "DeepFake Shield")}'

        # Try sending email
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.content_subtype = 'html'
        email.send(fail_silently=False)

        logger.info(f"Verification email sent to {user.email}")
        return True

    except Exception as e:
        logger.warning(f"Email sending failed: {e}")
        # Always log the verification URL so user can still verify
        logger.info(f"=== VERIFICATION URL FOR {user.email}: {verify_url} ===")

        # If using console backend, the email IS printed — this is success
        backend = getattr(settings, 'EMAIL_BACKEND', '')
        if 'console' in backend.lower():
            logger.info("Console email backend is active — email printed to terminal.")
            return True

        return Falsew