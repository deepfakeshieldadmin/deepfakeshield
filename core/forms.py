"""
Forms for DeepFake Shield — signup, login, uploads, text scan,
change password, forgot/reset password.
"""
import random
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
from django.conf import settings
from .captcha_utils import generate_image_captcha, generate_math_captcha


class StrongCaptchaMixin:
    """Mixin to add strong image CAPTCHA to forms."""

    def setup_captcha(self, request):
        try:
            captcha_text, captcha_image_src, _ = generate_image_captcha()
            request.session['captcha_answer'] = captcha_text.upper()
            request.session.modified = True
            return {'captcha_type': 'image', 'captcha_image': captcha_image_src, 'captcha_question': None}
        except Exception:
            question, answer, _ = generate_math_captcha()
            request.session['captcha_answer'] = str(answer)
            request.session.modified = True
            return {'captcha_type': 'math', 'captcha_image': None, 'captcha_question': question}

    def validate_captcha(self, request, user_answer):
        expected = request.session.get('captcha_answer', '')
        if not expected:
            return False
        return str(user_answer).strip().upper() == expected.upper()


class SignupForm(forms.Form, StrongCaptchaMixin):
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
            'style': 'letter-spacing:3px;font-weight:700;text-transform:uppercase;font-size:1.1rem;',
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
            'style': 'letter-spacing:3px;font-weight:700;text-transform:uppercase;font-size:1.1rem;',
        })
    )


# ══════════════════════════════════════════════════════════
# CHANGE PASSWORD — Option 1: via Old Password (logged-in)
# ══════════════════════════════════════════════════════════
class ChangePasswordForm(forms.Form):
    """Change password using old password verification. Requires user to be logged in."""

    old_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your current password',
            'autocomplete': 'current-password',
            'id': 'id_old_password',
        })
    )
    new_password1 = forms.CharField(
        label='New Password',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password (min 8 characters)',
            'autocomplete': 'new-password',
            'id': 'id_new_password1',
        })
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your new password',
            'autocomplete': 'new-password',
            'id': 'id_new_password2',
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_pw = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_pw):
            raise forms.ValidationError('Your current password is incorrect.')
        return old_pw

    def clean_new_password1(self):
        pw = self.cleaned_data.get('new_password1')
        if pw:
            password_validation.validate_password(pw, self.user)
        return pw

    def clean(self):
        cleaned = super().clean()
        pw1 = cleaned.get('new_password1')
        pw2 = cleaned.get('new_password2')
        old = cleaned.get('old_password')
        if pw1 and pw2 and pw1 != pw2:
            self.add_error('new_password2', 'New passwords do not match.')
        if pw1 and old and pw1 == old:
            self.add_error('new_password1', 'New password must be different from your current password.')
        return cleaned

    def save(self):
        """Save the new password and return the user."""
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        self.user.save()
        return self.user


# ══════════════════════════════════════════════════════════
# FORGOT PASSWORD — Option 2: via Email
# ══════════════════════════════════════════════════════════
class ForgotPasswordForm(forms.Form):
    """Request a password reset link via registered email."""

    email = forms.EmailField(
        label='Registered Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your registered email address',
            'autocomplete': 'email',
            'id': 'id_forgot_email',
        })
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        # We don't reveal if email exists (security best practice)
        # Just validate the format — actual check is in the view
        return email.lower().strip()


class ResetPasswordForm(forms.Form):
    """Set new password after clicking email reset link."""

    new_password1 = forms.CharField(
        label='New Password',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password (min 8 characters)',
            'autocomplete': 'new-password',
            'id': 'id_reset_pw1',
        })
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your new password',
            'autocomplete': 'new-password',
            'id': 'id_reset_pw2',
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_password1(self):
        pw = self.cleaned_data.get('new_password1')
        if pw:
            password_validation.validate_password(pw, self.user)
        return pw

    def clean(self):
        cleaned = super().clean()
        pw1 = cleaned.get('new_password1')
        pw2 = cleaned.get('new_password2')
        if pw1 and pw2 and pw1 != pw2:
            self.add_error('new_password2', 'Passwords do not match.')
        return cleaned

    def save(self):
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        self.user.save()
        return self.user


# ══════════════════════════════════════════════════════════
# UPLOAD FORMS (unchanged)
# ══════════════════════════════════════════════════════════
class ImageUploadForm(forms.Form):
    image = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'form-control', 'accept': 'image/*', 'id': 'file-input',
        }),
        help_text='Supported: JPG, PNG, BMP, WebP, TIFF. Max 20MB.'
    )

    def clean_image(self):
        f = self.cleaned_data['image']
        max_bytes = settings.DEEPFAKE_SHIELD['MAX_IMAGE_SIZE_MB'] * 1024 * 1024
        if f.size > max_bytes:
            raise forms.ValidationError(f'Image too large. Max {settings.DEEPFAKE_SHIELD["MAX_IMAGE_SIZE_MB"]}MB.')
        ext = f.name.rsplit('.', 1)[-1].lower() if '.' in f.name else ''
        supported = [x.lower().strip('.') for x in settings.DEEPFAKE_SHIELD['SUPPORTED_IMAGE_FORMATS']]
        if ext not in supported:
            raise forms.ValidationError(f'Unsupported format ".{ext}". Allowed: {", ".join(supported).upper()}')
        return f


class VideoUploadForm(forms.Form):
    video = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control', 'accept': 'video/*', 'id': 'file-input',
        }),
        help_text='Supported: MP4, AVI, MOV, MKV, WebM. Max 100MB.'
    )

    def clean_video(self):
        f = self.cleaned_data['video']
        max_bytes = settings.DEEPFAKE_SHIELD['MAX_VIDEO_SIZE_MB'] * 1024 * 1024
        if f.size > max_bytes:
            raise forms.ValidationError(f'Video too large. Max {settings.DEEPFAKE_SHIELD["MAX_VIDEO_SIZE_MB"]}MB.')
        ext = f.name.rsplit('.', 1)[-1].lower() if '.' in f.name else ''
        supported = [x.lower().strip('.') for x in settings.DEEPFAKE_SHIELD['SUPPORTED_VIDEO_FORMATS']]
        if ext not in supported:
            raise forms.ValidationError(f'Unsupported format ".{ext}". Allowed: {", ".join(supported).upper()}')
        return f


class AudioUploadForm(forms.Form):
    audio = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control', 'accept': 'audio/*', 'id': 'file-input',
        }),
        help_text='Supported: WAV, MP3, FLAC, OGG, M4A. Max 50MB.'
    )

    def clean_audio(self):
        f = self.cleaned_data['audio']
        max_bytes = settings.DEEPFAKE_SHIELD['MAX_AUDIO_SIZE_MB'] * 1024 * 1024
        if f.size > max_bytes:
            raise forms.ValidationError(f'Audio too large. Max {settings.DEEPFAKE_SHIELD["MAX_AUDIO_SIZE_MB"]}MB.')
        ext = f.name.rsplit('.', 1)[-1].lower() if '.' in f.name else ''
        supported = [x.lower().strip('.') for x in settings.DEEPFAKE_SHIELD['SUPPORTED_AUDIO_FORMATS']]
        if ext not in supported:
            raise forms.ValidationError(f'Unsupported format ".{ext}". Allowed: {", ".join(supported).upper()}')
        return f


class TextScanForm(forms.Form):
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Paste or type the text you want to analyze...',
            'rows': 10, 'id': 'text-input', 'maxlength': 50000,
        }),
        max_length=50000, min_length=50,
        help_text='Minimum 50 characters, maximum 50,000.'
    )


class ResendVerificationForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your registered email',
        })
    )