"""
Forms for DeepFake Shield — signup, login, uploads, text scan.
Includes strong image-based CAPTCHA.
FIXED: Extension check no longer adds dot prefix — was causing
       "Unsupported image format" even for valid JPG/PNG files.
"""
import random
from django import forms
from django.contrib.auth.models import User
from django.conf import settings
from .captcha_utils import generate_image_captcha, generate_math_captcha


class StrongCaptchaMixin:
    """Mixin to add strong image CAPTCHA to forms."""

    def setup_captcha(self, request):
        """Generate CAPTCHA and store answer in session. Returns template context."""
        try:
            captcha_text, captcha_image_src, _ = generate_image_captcha()
            request.session['captcha_answer'] = captcha_text.upper()
            request.session.modified = True
            return {
                'captcha_type': 'image',
                'captcha_image': captcha_image_src,
                'captcha_question': None,
            }
        except Exception:
            question, answer, _ = generate_math_captcha()
            request.session['captcha_answer'] = str(answer)
            request.session.modified = True
            return {
                'captcha_type': 'math',
                'captcha_image': None,
                'captcha_question': question,
            }

    def validate_captcha(self, request, user_answer):
        """Validate CAPTCHA answer."""
        expected = request.session.get('captcha_answer', '')
        if not expected:
            return False
        return str(user_answer).strip().upper() == expected.upper()


class SignupForm(forms.Form, StrongCaptchaMixin):
    """User registration form."""

    username = forms.CharField(
        max_length=150, min_length=3,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username',
            'autocomplete': 'username',
        }),
        help_text='3-150 characters.'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email',
        })
    )
    password1 = forms.CharField(
        label='Password', min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a password (min 8 characters)',
            'autocomplete': 'new-password',
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password',
        })
    )
    captcha = forms.CharField(
        label='CAPTCHA',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter the code shown above',
            'autocomplete': 'off',
            'style': 'letter-spacing: 3px; font-weight: 700; text-transform: uppercase; font-size: 1.1rem;',
        })
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Passwords do not match.')
        return cleaned


class LoginForm(forms.Form, StrongCaptchaMixin):
    """Login form."""

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
        })
    )
    captcha = forms.CharField(
        label='CAPTCHA',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter the code shown above',
            'autocomplete': 'off',
            'style': 'letter-spacing: 3px; font-weight: 700; text-transform: uppercase; font-size: 1.1rem;',
        })
    )


class ImageUploadForm(forms.Form):
    image = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'id': 'file-input',
        }),
        help_text='Supported: JPG, PNG, BMP, WebP, TIFF. Max 20MB.'
    )

    def clean_image(self):
        f = self.cleaned_data['image']

        # ── Size check ──
        max_bytes = settings.DEEPFAKE_SHIELD['MAX_IMAGE_SIZE_MB'] * 1024 * 1024
        if f.size > max_bytes:
            raise forms.ValidationError(
                f'Image too large. Maximum size is {settings.DEEPFAKE_SHIELD["MAX_IMAGE_SIZE_MB"]}MB.'
            )

        # ── Format check (BUG FIX: strip dot before comparing) ──
        # f.name gives e.g. "photo.JPG"
        # ext becomes "jpg" (lowercase, no dot)
        # supported list is ['jpg','jpeg','png',...] — no dots
        ext = f.name.rsplit('.', 1)[-1].lower() if '.' in f.name else ''
        supported = [fmt.lower().strip('.') for fmt in settings.DEEPFAKE_SHIELD['SUPPORTED_IMAGE_FORMATS']]
        if ext not in supported:
            raise forms.ValidationError(
                f'Unsupported format ".{ext}". Allowed: {", ".join(supported).upper()}'
            )

        return f


class VideoUploadForm(forms.Form):
    video = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'video/*',
            'id': 'file-input',
        }),
        help_text='Supported: MP4, AVI, MOV, MKV, WebM. Max 100MB.'
    )

    def clean_video(self):
        f = self.cleaned_data['video']

        # ── Size check ──
        max_bytes = settings.DEEPFAKE_SHIELD['MAX_VIDEO_SIZE_MB'] * 1024 * 1024
        if f.size > max_bytes:
            raise forms.ValidationError(
                f'Video too large. Maximum size is {settings.DEEPFAKE_SHIELD["MAX_VIDEO_SIZE_MB"]}MB.'
            )

        # ── Format check (no dot prefix) ──
        ext = f.name.rsplit('.', 1)[-1].lower() if '.' in f.name else ''
        supported = [fmt.lower().strip('.') for fmt in settings.DEEPFAKE_SHIELD['SUPPORTED_VIDEO_FORMATS']]
        if ext not in supported:
            raise forms.ValidationError(
                f'Unsupported format ".{ext}". Allowed: {", ".join(supported).upper()}'
            )

        return f


class AudioUploadForm(forms.Form):
    audio = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'audio/*',
            'id': 'file-input',
        }),
        help_text='Supported: WAV, MP3, FLAC, OGG, M4A. Max 50MB.'
    )

    def clean_audio(self):
        f = self.cleaned_data['audio']

        # ── Size check ──
        max_bytes = settings.DEEPFAKE_SHIELD['MAX_AUDIO_SIZE_MB'] * 1024 * 1024
        if f.size > max_bytes:
            raise forms.ValidationError(
                f'Audio too large. Maximum size is {settings.DEEPFAKE_SHIELD["MAX_AUDIO_SIZE_MB"]}MB.'
            )

        # ── Format check (no dot prefix) ──
        ext = f.name.rsplit('.', 1)[-1].lower() if '.' in f.name else ''
        supported = [fmt.lower().strip('.') for fmt in settings.DEEPFAKE_SHIELD['SUPPORTED_AUDIO_FORMATS']]
        if ext not in supported:
            raise forms.ValidationError(
                f'Unsupported format ".{ext}". Allowed: {", ".join(supported).upper()}'
            )

        return f


class TextScanForm(forms.Form):
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Paste or type the text you want to analyze...',
            'rows': 10,
            'id': 'text-input',
            'maxlength': 50000,
        }),
        max_length=50000,
        min_length=50,
        help_text='Minimum 50 characters, maximum 50,000.'
    )


class ResendVerificationForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your registered email',
        })
    )