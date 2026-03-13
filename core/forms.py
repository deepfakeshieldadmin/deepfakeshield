from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
import random
import string
import re


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control auth-input',
            'placeholder': 'Enter your email',
            'autocomplete': 'email',
        })
    )

    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control auth-input',
            'placeholder': 'First Name',
        })
    )

    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control auth-input',
            'placeholder': 'Last Name',
        })
    )

    captcha_answer = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control auth-input',
            'placeholder': 'Enter CAPTCHA answer',
            'autocomplete': 'off',
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        self.captcha_question = kwargs.pop('captcha_question', None)
        self.captcha_correct = kwargs.pop('captcha_correct', None)
        super().__init__(*args, **kwargs)

        self.fields['username'].widget = forms.TextInput(attrs={
            'class': 'form-control auth-input',
            'placeholder': 'Choose a username',
            'autocomplete': 'username',
        })

        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control auth-input',
            'placeholder': 'Create Password',
            'autocomplete': 'new-password',
        })

        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control auth-input',
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password',
        })

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        if not re.match(pattern, email):
            raise forms.ValidationError("No valid email detected. Please enter a valid email.")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_captcha_answer(self):
        answer = self.cleaned_data.get('captcha_answer', '').strip()
        if self.captcha_correct and str(answer).lower() != str(self.captcha_correct).lower():
            raise forms.ValidationError("Incorrect CAPTCHA answer.")
        return answer


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control auth-input',
            'placeholder': 'Username',
            'autocomplete': 'username',
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control auth-input',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
        })
    )


class ImageUploadForm(forms.Form):
    image = forms.ImageField(
        required=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'bmp', 'webp', 'tiff'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and image.size > 20 * 1024 * 1024:
            raise forms.ValidationError('Image file too large. Maximum size is 20MB.')
        return image


class VideoUploadForm(forms.Form):
    video = forms.FileField(
        required=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov', 'mkv', 'webm'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'video/*'})
    )

    def clean_video(self):
        video = self.cleaned_data.get('video')
        if video and video.size > 50 * 1024 * 1024:
            raise forms.ValidationError('Video file too large. Maximum size is 50MB.')
        return video


class AudioUploadForm(forms.Form):
    audio = forms.FileField(
        required=True,
        validators=[FileExtensionValidator(allowed_extensions=['wav', 'mp3', 'ogg', 'flac', 'aac'])],
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'audio/*'})
    )

    def clean_audio(self):
        audio = self.cleaned_data.get('audio')
        if audio and audio.size > 30 * 1024 * 1024:
            raise forms.ValidationError('Audio file too large. Maximum size is 30MB.')
        return audio


class TextAnalysisForm(forms.Form):
    text = forms.CharField(
        required=True,
        min_length=50,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Paste the text you want to analyze here... (minimum 50 characters)',
            'rows': 10,
        })
    )

    def clean_text(self):
        text = self.cleaned_data.get('text', '').strip()
        if len(text) < 50:
            raise forms.ValidationError('Please enter at least 50 characters.')
        if len(text) > 50000:
            raise forms.ValidationError('Text too long. Maximum 50,000 characters.')
        return text


def generate_captcha():
    captcha_type = random.choice(['math_add', 'math_sub', 'math_mult', 'alphanumeric'])

    if captcha_type == 'math_add':
        a = random.randint(10, 99)
        b = random.randint(10, 99)
        return f"What is {a} + {b}?", str(a + b)

    if captcha_type == 'math_sub':
        a = random.randint(50, 150)
        b = random.randint(10, 49)
        return f"What is {a} - {b}?", str(a - b)

    if captcha_type == 'math_mult':
        a = random.randint(3, 15)
        b = random.randint(2, 12)
        return f"What is {a} × {b}?", str(a * b)

    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"Type this code exactly: {code}", code