from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_verification_email(user, token_obj, request=None):
    try:
        if request:
            protocol = 'https' if request.is_secure() else 'http'
            domain = request.get_host()
        else:
            protocol = 'http'
            domain = '127.0.0.1:8000'

        verification_url = f"{protocol}://{domain}/email/verify/{token_obj.token}/"

        html_message = render_to_string('emails/verify_email.html', {
            'user': user,
            'verification_url': verification_url,
        })
        plain_message = strip_tags(html_message)

        send_mail(
            subject='Verify Your DeepFake Shield Account',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception:
        return False