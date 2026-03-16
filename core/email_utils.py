"""
Email utilities — with timeout to prevent worker crash.
"""
import logging
import threading
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

logger = logging.getLogger(__name__)


def _send_email_thread(subject, html_body, from_email, to_email):
    """Send email in a separate thread so it doesn't block the request."""
    try:
        email = EmailMessage(
            subject=subject,
            body=html_body,
            from_email=from_email,
            to=[to_email],
        )
        email.content_subtype = 'html'
        # Set a 10-second timeout on the connection
        import socket
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(10)
        try:
            email.send(fail_silently=False)
            logger.info(f"✅ Email sent to {to_email}")
        finally:
            socket.setdefaulttimeout(old_timeout)
    except Exception as e:
        logger.error(f"❌ Email thread failed for {to_email}: {e}")


def send_verification_email(user, token, request):
    """Send verification email without blocking the request."""
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
        subject = 'Verify your email - DeepFake Shield'
        from_email = settings.DEFAULT_FROM_EMAIL

        logger.info(f"Sending email to {user.email} via {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        logger.info(f"Verify URL: {verify_url}")

        # Send in background thread — don't block the HTTP request
        thread = threading.Thread(
            target=_send_email_thread,
            args=(subject, html_message, from_email, user.email),
            daemon=True
        )
        thread.start()

        return True, None

    except Exception as e:
        logger.error(f"❌ Email setup failed: {e}")
        return False, str(e)