"""
Database models for DeepFake Shield.
Stores scan results, email verification tokens, and user profiles.
"""
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ScanResult(models.Model):
    """Stores all media scan results with full analysis data."""

    SCAN_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('text', 'Text'),
    ]

    CLASSIFICATION_CHOICES = [
        ('highly_authentic', 'Highly Authentic'),
        ('likely_real', 'Likely Real'),
        ('suspicious', 'Suspicious'),
        ('likely_fake', 'Likely Fake'),
        ('ai_generated', 'AI Generated'),
        ('deepfake', 'DeepFake'),
        ('edited', 'Edited'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='scan_results',
        db_index=True
    )
    scan_type = models.CharField(max_length=10, choices=SCAN_TYPE_CHOICES, db_index=True)
    original_filename = models.CharField(max_length=500, blank=True, default='')
    uploaded_file = models.FileField(upload_to='uploads/%Y/%m/%d/', blank=True, null=True)
    processed_file = models.FileField(upload_to='processed/%Y/%m/%d/', blank=True, null=True)
    report_file = models.FileField(upload_to='reports/%Y/%m/%d/', blank=True, null=True)
    submitted_text = models.TextField(blank=True, default='')

    # Analysis results
    authenticity_score = models.FloatField(default=0.0)
    classification = models.CharField(
        max_length=100,
        choices=CLASSIFICATION_CHOICES,
        default='suspicious'
    )
    real_vs_fake = models.CharField(max_length=255, default='Unknown')
    explanation = models.TextField(blank=True, default='')
    summary = models.TextField(blank=True, default='')
    description = models.TextField(blank=True, default='')
    detailed_results = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Scan Result'
        verbose_name_plural = 'Scan Results'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['scan_type', '-created_at']),
        ]

    def __str__(self):
        return f"{self.scan_type.upper()} Scan - {self.original_filename or 'Text'} - {self.authenticity_score:.1f}%"

    @classmethod
    def get_real_vs_fake(cls, score):
        """Get real vs fake label from score."""
        if score >= 90:
            return 'Authentic — No manipulation detected'
        elif score >= 70:
            return 'Likely Real — No manipulation found'
        elif score >= 40:
            return 'Suspicious — Possible manipulation'
        return 'Likely Fake / Manipulated'
    
    @property
    def score_label(self):
        if self.authenticity_score >= 90:
            return 'Highly Authentic'
        elif self.authenticity_score >= 70:
            return 'Likely Real'
        elif self.authenticity_score >= 40:
            return 'Suspicious'
        return 'Likely Fake'

    @property
    def score_color(self):
        if self.authenticity_score >= 70:
            return 'success'
        elif self.authenticity_score >= 40:
            return 'warning'
        return 'danger'

    @classmethod
    def classify_score(cls, score):
        if score >= 90: return 'highly_authentic'
        elif score >= 70: return 'likely_real'
        elif score >= 40: return 'suspicious'
        return 'likely_fake'


class EmailVerificationToken(models.Model):
    """Token for email verification during signup."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='email_verification_token'
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Email Verification Token'
        verbose_name_plural = 'Email Verification Tokens'

    def __str__(self):
        return f"Verification for {self.user.username}"

    @property
    def is_expired(self):
        """Token expires after 24 hours."""
        return timezone.now() > self.created_at + timezone.timedelta(hours=24)

    @property
    def is_valid(self):
        """Check if token is valid (not used and not expired)."""
        return not self.is_used and not self.is_expired


class UserProfile(models.Model):
    """Extended user profile with preferences."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_email_verified = models.BooleanField(default=False)
    total_scans = models.PositiveIntegerField(default=0)
    preferred_theme = models.CharField(max_length=10, default='dark')
    preferred_language = models.CharField(max_length=10, default='en')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"Profile: {self.user.username}"

    def increment_scans(self):
        self.total_scans += 1
        self.save(update_fields=['total_scans'])