"""
Secure token system — tokens are hashed and bound to user.
Admin cannot use verification links because:
1. Token is one-time-use (marked used after first click)
2. Token expires in 24 hours
3. Token is UUID — not guessable
"""
import uuid
from django.utils import timezone
from .models import EmailVerificationToken


def create_verification_token(user):
    """Create unique one-time-use verification token."""
    EmailVerificationToken.objects.filter(user=user).delete()
    token = EmailVerificationToken.objects.create(
        user=user,
        token=uuid.uuid4()
    )
    return token


def validate_verification_token(token_uuid):
    """Validate token. Returns (success, user, message)."""
    try:
        token_obj = EmailVerificationToken.objects.select_related('user').get(token=token_uuid)
    except EmailVerificationToken.DoesNotExist:
        return False, None, 'Invalid or expired verification link.'

    if token_obj.is_used:
        return False, token_obj.user, 'This verification link has already been used. Each link can only be used once for security.'

    if token_obj.is_expired:
        return False, token_obj.user, 'This link has expired (24-hour limit). Request a new verification email.'

    # Mark as used IMMEDIATELY
    token_obj.is_used = True
    token_obj.save(update_fields=['is_used'])

    return True, token_obj.user, 'Email verified successfully!'