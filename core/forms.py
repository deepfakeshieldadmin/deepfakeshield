"""
DeepFake Shield — Forms
All forms for authentication, uploads, and text scanning.
"""

from django import forms
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
import random


class LoginForm(forms.Form):
    """Login form with captcha."""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email',
            'id': 'id_username',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'id': 'id_password',
            'autocomplete': 'current-password',
        })
    )
    captcha = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your answer',
            'autocomplete': 'off',
        })
    )


class SignupForm(forms.Form):
    """Registration form with email, password confirmation, and captcha."""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username',
            'id': 'id_username',
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com',
            'id': 'id_email',
        })
    )
    password1 = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create password (min 6 chars)',
            'id': 'id_password1',
        })
    )
    password2 = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'id': 'id_password2',
        })
    )
    captcha = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your answer',
            'autocomplete': 'off',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data


class ImageUploadForm(forms.Form):
    """Image file upload form."""
    file = forms.FileField(
        validators=[FileExtensionValidator(
            allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'bmp', 'tiff']
        )],
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
        })
    )


class VideoUploadForm(forms.Form):
    """Video file upload form."""
    file = forms.FileField(
        validators=[FileExtensionValidator(
            allowed_extensions=['mp4', 'mov', 'avi', 'mkv', 'webm']
        )],
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'video/*',
        })
    )


class AudioUploadForm(forms.Form):
    """Audio file upload form."""
    file = forms.FileField(
        validators=[FileExtensionValidator(
            allowed_extensions=['wav', 'mp3', 'ogg', 'flac', 'm4a']
        )],
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'audio/*',
        })
    )


class TextScanForm(forms.Form):
    """Text input form for AI text detection."""
    text = forms.CharField(
        min_length=20,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Paste your text here for authenticity analysis... (minimum 20 characters)',
            'id': 'id_text',
        })
    )


class ResendVerificationForm(forms.Form):
    """Form for resending email verification."""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com',
        })
    )