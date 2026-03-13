import re
from django.core.mail import EmailMultiAlternatives
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from .tokens import email_verification_token


def is_valid_email(email):
    if not email:
        return False
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return bool(re.match(pattern, email))


def build_base_url(request):
    """
    Uses SITE_BASE_URL from settings if present.
    Otherwise falls back to request host.
    """
    site_base_url = getattr(settings, 'SITE_BASE_URL', '').strip()
    if site_base_url:
        return site_base_url.rstrip('/')

    protocol = 'https' if request.is_secure() else 'http'
    return f"{protocol}://{request.get_host()}"


def send_verification_email(request, user):
    try:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_verification_token.make_token(user)

        base_url = build_base_url(request)
        verification_link = f"{base_url}/verify-email/{uid}/{token}/"

        subject = "Verify Your Email - Deep Fake Shield"

        text_content = f"""
Hello {user.first_name or user.username},

Welcome to Deep Fake Shield.

Please verify your email by clicking this link:

{verification_link}

After clicking the link, your account will become verified.

If you did not create this account, ignore this email.

- Deep Fake Shield
"""

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Verify Your Email</title>
</head>
<body style="margin:0;padding:0;background:#f4f7fc;font-family:Arial,sans-serif;">
    <div style="max-width:600px;margin:40px auto;background:#ffffff;border-radius:18px;overflow:hidden;box-shadow:0 8px 30px rgba(0,0,0,0.08);">
        <div style="background:linear-gradient(135deg,#007bff,#6f42c1);padding:35px 25px;text-align:center;">
            <div style="font-size:48px;margin-bottom:10px;">🛡️</div>
            <h1 style="margin:0;color:#ffffff;font-size:26px;">Deep Fake Shield</h1>
            <p style="margin:8px 0 0;color:rgba(255,255,255,0.85);font-size:14px;">
                Real-Time Media Authenticity Verification
            </p>
        </div>

        <div style="padding:35px 28px;">
            <h2 style="margin-top:0;color:#1a1a2e;">Verify Your Email</h2>
            <p style="font-size:15px;color:#555;line-height:1.7;">
                Hello <strong>{user.first_name or user.username}</strong>,
            </p>
            <p style="font-size:15px;color:#555;line-height:1.7;">
                Please click the button below to verify your email address.
            </p>

            <div style="text-align:center;margin:30px 0;">
                <a href="{verification_link}" style="display:inline-block;padding:14px 30px;background:linear-gradient(135deg,#007bff,#6f42c1);color:#fff;text-decoration:none;border-radius:10px;font-weight:bold;font-size:16px;">
                    Verify My Email
                </a>
            </div>

            <p style="font-size:13px;color:#777;line-height:1.6;">
                If the button does not work, copy and paste this link into your browser:
            </p>
            <p style="font-size:12px;color:#007bff;word-break:break-all;background:#f7faff;padding:12px;border-radius:8px;">
                {verification_link}
            </p>

            <p style="font-size:13px;color:#777;line-height:1.6;margin-top:25px;">
                After clicking the link, your account will be marked as <strong>verified</strong>.
            </p>
        </div>
    </div>
</body>
</html>
"""

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        print(f"Verification email successfully sent to {user.email}")
        return True

    except Exception as e:
        print(f"EMAIL ERROR: {str(e)}")
        return False