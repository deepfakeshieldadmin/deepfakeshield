import json
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class EmailVerificationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.token}"

    def is_expired(self):
        from datetime import timedelta
        return timezone.now() > self.created_at + timedelta(hours=24)

    class Meta:
        ordering = ['-created_at']


class ScanResult(models.Model):
    SCAN_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('text', 'Text'),
    ]

    CLASSIFICATION_CHOICES = [
        ('authentic', 'Highly Authentic'),
        ('likely_real', 'Likely Real'),
        ('suspicious', 'Suspicious'),
        ('likely_fake', 'Likely Fake'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scan_results')
    scan_type = models.CharField(max_length=20, choices=SCAN_TYPE_CHOICES)

    original_filename = models.CharField(max_length=500, blank=True, default='')
    uploaded_file = models.FileField(upload_to='uploads/%Y/%m/', blank=True, null=True)
    processed_file = models.FileField(upload_to='processed/%Y/%m/', blank=True, null=True)
    report_file = models.FileField(upload_to='reports/%Y/%m/', blank=True, null=True)

    submitted_text = models.TextField(blank=True, default='')

    authenticity_score = models.IntegerField(default=0)
    classification = models.CharField(max_length=20, choices=CLASSIFICATION_CHOICES, default='suspicious')
    explanation = models.TextField(blank=True, default='')
    detailed_results = models.TextField(blank=True, default='{}')

    file_size = models.BigIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_detailed_results(self, data):
        self.detailed_results = json.dumps(data, default=str)

    def get_detailed_results(self):
        try:
            return json.loads(self.detailed_results)
        except Exception:
            return {}

    @property
    def classification_display(self):
        labels = {
            'authentic': 'Highly Authentic',
            'likely_real': 'Likely Real',
            'suspicious': 'Possibly Edited / Suspicious',
            'likely_fake': 'Likely Fake / AI Generated',
        }
        return labels.get(self.classification, self.classification)

    @property
    def score_color(self):
        if self.authenticity_score >= 90:
            return 'success'
        elif self.authenticity_score >= 75:
            return 'info'
        elif self.authenticity_score >= 40:
            return 'warning'
        return 'danger'

    @property
    def score_dashoffset(self):
        circumference = 326.72
        offset = circumference - (self.authenticity_score / 100.0) * circumference
        return round(offset, 2)

    def __str__(self):
        return f"{self.scan_type} - {self.original_filename} - {self.authenticity_score}"

    class Meta:
        ordering = ['-created_at']