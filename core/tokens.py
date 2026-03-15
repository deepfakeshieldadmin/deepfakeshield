"""
Token generation and validation for email verification.
"""
import uuid
from django.utils import timezone
from .models import EmailVerificationToken


def create_verification_token(user):
    """Create or refresh an email verification token for a user."""
    # Delete any existing token
    EmailVerificationToken.objects.filter(user=user).delete()

    # Create new token
    token = EmailVerificationToken.objects.create(
        user=user,
        token=uuid.uuid4()
    )
    return token


def validate_verification_token(token_uuid):
    """Validate a verification token. Returns (success, user, message)."""
    try:
        token_obj = EmailVerificationToken.objects.select_related('user').get(token=token_uuid)
    except EmailVerificationToken.DoesNotExist:
        return False, None, 'Invalid verification link.'

    if token_obj.is_used:
        return False, token_obj.user, 'This link has already been used.'

    if token_obj.is_expired:
        return False, token_obj.user, 'This verification link has expired. Please request a new one.'

    # Mark as used
    token_obj.is_used = True
    token_obj.save(update_fields=['is_used'])

    return True, token_obj.user, 'Email verified successfully!'