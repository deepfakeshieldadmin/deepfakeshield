"""
Database models for DeepFakeShield.
Stores scan history for images, videos, audio, and text.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import os


def upload_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('uploads/images/', filename)


def upload_video_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('uploads/videos/', filename)


def upload_audio_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('uploads/audio/', filename)


class ImageScan(models.Model):
    """Stores image scan results."""
    CLASSIFICATION_CHOICES = [
        ('authentic', 'Highly Authentic'),
        ('likely_real', 'Likely Real'),
        ('suspicious', 'Possibly Edited / Suspicious'),
        ('likely_fake', 'Likely AI Generated / Fake'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='image_scans')
    image = models.ImageField(upload_to=upload_image_path)
    original_filename = models.CharField(max_length=255, default='unknown')
    authenticity_score = models.FloatField(default=0.0)
    classification = models.CharField(max_length=20, choices=CLASSIFICATION_CHOICES, default='suspicious')
    is_ai_generated = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    face_count = models.IntegerField(default=0)
    has_exif = models.BooleanField(default=False)
    exif_data = models.JSONField(default=dict, blank=True)
    analysis_details = models.JSONField(default=dict, blank=True)
    explanation = models.TextField(default='', blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Image Scan'
        verbose_name_plural = 'Image Scans'

    def __str__(self):
        return f"ImageScan({self.original_filename}) - {self.authenticity_score}%"


class VideoScan(models.Model):
    """Stores video scan results."""
    CLASSIFICATION_CHOICES = [
        ('authentic', 'Highly Authentic'),
        ('likely_real', 'Likely Real'),
        ('suspicious', 'Possibly Edited / Suspicious'),
        ('likely_fake', 'Likely AI Generated / Fake'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_scans')
    video = models.FileField(upload_to=upload_video_path)
    original_filename = models.CharField(max_length=255, default='unknown')
    authenticity_score = models.FloatField(default=0.0)
    classification = models.CharField(max_length=20, choices=CLASSIFICATION_CHOICES, default='suspicious')
    total_frames_analyzed = models.IntegerField(default=0)
    frame_scores = models.JSONField(default=list, blank=True)
    analysis_details = models.JSONField(default=dict, blank=True)
    explanation = models.TextField(default='', blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Video Scan'
        verbose_name_plural = 'Video Scans'

    def __str__(self):
        return f"VideoScan({self.original_filename}) - {self.authenticity_score}%"


class AudioScan(models.Model):
    """Stores audio scan results."""
    CLASSIFICATION_CHOICES = [
        ('authentic', 'Highly Authentic'),
        ('likely_real', 'Likely Real'),
        ('suspicious', 'Possibly Edited / Suspicious'),
        ('likely_fake', 'Likely AI Generated / Fake'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audio_scans')
    audio = models.FileField(upload_to=upload_audio_path)
    original_filename = models.CharField(max_length=255, default='unknown')
    authenticity_score = models.FloatField(default=0.0)
    classification = models.CharField(max_length=20, choices=CLASSIFICATION_CHOICES, default='suspicious')
    duration_seconds = models.FloatField(default=0.0)
    analysis_details = models.JSONField(default=dict, blank=True)
    explanation = models.TextField(default='', blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Audio Scan'
        verbose_name_plural = 'Audio Scans'

    def __str__(self):
        return f"AudioScan({self.original_filename}) - {self.authenticity_score}%"


class TextScan(models.Model):
    """Stores text scan results."""
    CLASSIFICATION_CHOICES = [
        ('authentic', 'Highly Authentic'),
        ('likely_real', 'Likely Real'),
        ('suspicious', 'Possibly Edited / Suspicious'),
        ('likely_fake', 'Likely AI Generated / Fake'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='text_scans')
    input_text = models.TextField()
    word_count = models.IntegerField(default=0)
    authenticity_score = models.FloatField(default=0.0)
    classification = models.CharField(max_length=20, choices=CLASSIFICATION_CHOICES, default='suspicious')
    analysis_details = models.JSONField(default=dict, blank=True)
    explanation = models.TextField(default='', blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Text Scan'
        verbose_name_plural = 'Text Scans'

    def __str__(self):
        return f"TextScan({self.word_count} words) - {self.authenticity_score}%"


class UserProfile(models.Model):
    """Extended user profile for preferences."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    theme = models.CharField(max_length=30, default='tech-blue')
    language = models.CharField(max_length=10, default='en')
    cursor_style = models.CharField(max_length=20, default='default')
    dark_mode = models.BooleanField(default=False)
    total_scans = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Profile({self.user.username})"
    
# ADD THIS AT THE VERY BOTTOM OF core/models.py
# (Keep all existing models above - do NOT delete anything)

class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification')
    is_verified = models.BooleanField(default=False)
    verification_sent_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {'Verified' if self.is_verified else 'Pending'}"