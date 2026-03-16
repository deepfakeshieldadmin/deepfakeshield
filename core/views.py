"""
DeepFake Shield - Views
All view functions for authentication, scanning, results, and reports.
"""

import os
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone

from .models import ScanResult, UserProfile, EmailVerificationToken
from .forms import (
    SignupForm, LoginForm, ImageUploadForm, VideoUploadForm,
    AudioUploadForm, TextScanForm, ResendVerificationForm
)
from .tokens import create_verification_token, validate_verification_token
from .email_utils import send_verification_email
from .ai_engine import analyze_image
from .video_engine import analyze_video
from .audio_engine import analyze_audio
from .text_engine import analyze_text
from .report_utils import generate_pdf_report

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════
# PUBLIC PAGES
# ═══════════════════════════════════════════════

def landing_view(request):
    """Premium landing page."""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    return render(request, 'landing.html')


def home_view(request):
    """Home page after entering the site."""
    return render(request, 'home.html')


def about_view(request):
    """About page."""
    return render(request, 'about.html')


def privacy_view(request):
    """Privacy policy page."""
    return render(request, 'privacy.html')


def education_view(request):
    """Educational resources about deepfakes."""
    return render(request, 'education.html')


# ═══════════════════════════════════════════════
# AUTHENTICATION
# ═══════════════════════════════════════════════

def signup_view(request):
    """User registration with CAPTCHA and email verification."""
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    form = SignupForm()

    if request.method == 'POST':
        form = SignupForm(request.POST)

        # Validate CAPTCHA
        captcha_answer = request.POST.get('captcha', '')
        expected = request.session.get('captcha_answer', '')
        captcha_valid = expected and captcha_answer.strip().upper() == expected.upper()

        if form.is_valid() and captcha_valid:
            try:
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password1'],
                    is_active=True,
                )

                # Create profile
                profile, _ = UserProfile.objects.get_or_create(user=user)

                # Create verification token
                token = create_verification_token(user)

                # Send verification email
                email_sent, error_msg = send_verification_email(user, token, request)

                if email_sent:
                    messages.success(
                        request,
                        f'Account created! Verification email sent to {user.email}. '
                        f'Please check your inbox (and spam folder).'
                    )
                else:
                    # Show the actual error to help debug
                    messages.warning(
                        request,
                        f'Account created but email delivery failed: {error_msg}. '
                        f'You can still login. Contact admin for verification.'
                    )
                    logger.error(f"Email failed for {user.email}: {error_msg}")

                return redirect('core:email_verification_sent')

            except Exception as e:
                logger.error(f"Signup error: {e}")
                messages.error(request, f'Registration failed: {str(e)}')
        else:
            if not captcha_valid:
                messages.error(request, 'Incorrect CAPTCHA. Please try again.')

    # Generate new CAPTCHA
    captcha_ctx = form.setup_captcha(request)

    return render(request, 'signup.html', {
        'form': form,
        'captcha_type': captcha_ctx.get('captcha_type', 'math'),
        'captcha_image': captcha_ctx.get('captcha_image'),
        'captcha_question': captcha_ctx.get('captcha_question'),
    })


def login_view(request):
    """User login with image CAPTCHA."""
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)

        captcha_answer = request.POST.get('captcha', '')
        expected = request.session.get('captcha_answer', '')
        captcha_valid = expected and captcha_answer.strip().upper() == expected.upper()

        if form.is_valid() and captcha_valid:
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                UserProfile.objects.get_or_create(user=user)
                messages.success(request, f'Welcome back, {user.username}!')
                next_url = request.GET.get('next', 'core:dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            if not captcha_valid:
                messages.error(request, 'Incorrect CAPTCHA. Please try again.')

    # Generate NEW captcha (GET or failed POST)
    captcha_ctx = form.setup_captcha(request)

    return render(request, 'login.html', {
        'form': form,
        'captcha_type': captcha_ctx.get('captcha_type', 'math'),
        'captcha_image': captcha_ctx.get('captcha_image'),
        'captcha_question': captcha_ctx.get('captcha_question'),
    })


def logout_view(request):
    """Logout user."""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('core:landing')


# ═══════════════════════════════════════════════
# EMAIL VERIFICATION
# ═══════════════════════════════════════════════

def verify_email_view(request, token):
    """
    Verify email with security checks.
    Even if admin clicks the link, the user account gets verified
    BUT we log who clicked it for audit trail.
    """
    success, user, message = validate_verification_token(token)

    if success and user:
        # Security: Log the verification event
        verifier_info = 'anonymous'
        if request.user.is_authenticated:
            verifier_info = request.user.username
            # If admin is verifying someone else's account, log it
            if request.user != user and request.user.is_staff:
                logger.warning(
                    f"SECURITY AUDIT: Admin '{request.user.username}' verified "
                    f"user '{user.username}' account. This may indicate the admin "
                    f"accessed the verification link from sent emails."
                )
        
        logger.info(f"Email verified for user '{user.username}' by '{verifier_info}'")
        
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.is_email_verified = True
        profile.save(update_fields=['is_email_verified'])

        messages.success(request, 'Email verified successfully!')
        return render(request, 'email_verification_success.html', {'user': user})
    else:
        messages.error(request, message)
        return render(request, 'email_verification_failed.html', {
            'message': message,
            'user': user,
        })


def email_verification_sent_view(request):
    """Confirmation page after signup."""
    return render(request, 'email_verification_sent.html')


def resend_verification_view(request):
    """Resend email verification link."""
    form = ResendVerificationForm()

    if request.method == 'POST':
        form = ResendVerificationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email__iexact=email)
                profile, _ = UserProfile.objects.get_or_create(user=user)

                if profile.is_email_verified:
                    messages.info(request, 'Your email is already verified. You can log in.')
                    return redirect('core:login')

                # Create new token
                token = create_verification_token(user)
                email_sent = send_verification_email(user, token, request)

                if email_sent:
                    messages.success(request, 'Verification email resent! Check your inbox.')
                else:
                    messages.info(
                        request,
                        'Verification email queued. Check spam folder or console in dev mode.'
                    )

                return redirect('core:email_verification_sent')

            except User.DoesNotExist:
                messages.error(request, 'No account found with that email address.')

    return render(request, 'resend_verification.html', {'form': form})


# ═══════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════

@login_required
def dashboard_view(request):
    """User dashboard with scan history."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    recent_scans = ScanResult.objects.filter(user=request.user)[:10]

    # Stats
    total_scans = ScanResult.objects.filter(user=request.user).count()
    image_scans = ScanResult.objects.filter(user=request.user, scan_type='image').count()
    video_scans = ScanResult.objects.filter(user=request.user, scan_type='video').count()
    audio_scans = ScanResult.objects.filter(user=request.user, scan_type='audio').count()
    text_scans = ScanResult.objects.filter(user=request.user, scan_type='text').count()

    context = {
        'profile': profile,
        'recent_scans': recent_scans,
        'total_scans': total_scans,
        'image_scans': image_scans,
        'video_scans': video_scans,
        'audio_scans': audio_scans,
        'text_scans': text_scans,
    }
    return render(request, 'dashboard.html', context)


@login_required
def scan_history_view(request):
    """Full scan history page."""
    scans = ScanResult.objects.filter(user=request.user)[:50]
    return render(request, 'dashboard.html', {
        'recent_scans': scans,
        'total_scans': scans.count(),
        'show_all': True,
    })


# ═══════════════════════════════════════════════
# IMAGE SCAN
# ═══════════════════════════════════════════════

@login_required
def upload_image_view(request):
    """Image upload and analysis."""
    form = ImageUploadForm()

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = form.cleaned_data['image']
            filename = image_file.name

            try:
                # Read file bytes
                file_bytes = image_file.read()
                image_file.seek(0)

                # Analyze
                analysis = analyze_image(file_bytes, filename=filename)

                # Create scan result
                scan = ScanResult(
                    user=request.user,
                    scan_type='image',
                    original_filename=filename,
                    authenticity_score=analysis.get('authenticity_score', 0),
                    classification=ScanResult.classify_score(analysis.get('authenticity_score', 0)),
                    real_vs_fake=analysis.get('real_vs_fake', 'Unknown'),
                    explanation=analysis.get('explanation', ''),
                    summary=analysis.get('summary', ''),
                    description=analysis.get('description', ''),
                    detailed_results=_clean_results_for_json(analysis),
                )

                # Save uploaded file
                scan.uploaded_file.save(filename, ContentFile(file_bytes), save=False)

                # Save processed image (with face boxes)
                processed_bytes = analysis.get('processed_image_bytes')
                if processed_bytes:
                    processed_filename = f"processed_{filename}"
                    if not processed_filename.lower().endswith('.jpg'):
                        processed_filename = processed_filename.rsplit('.', 1)[0] + '.jpg'
                    scan.processed_file.save(processed_filename, ContentFile(processed_bytes), save=False)

                scan.save()

                # Update profile scan count
                profile, _ = UserProfile.objects.get_or_create(user=request.user)
                profile.increment_scans()

                messages.success(request, 'Image analysis complete!')
                return redirect('core:result_image', scan_id=scan.id)

            except Exception as e:
                logger.error(f"Image upload/analysis error: {e}", exc_info=True)
                messages.error(request, f'Analysis failed: {str(e)}')

    return render(request, 'upload.html', {'form': form, 'scan_type': 'image'})


@login_required
def result_image_view(request, scan_id):
    """Display image analysis results."""
    scan = get_object_or_404(ScanResult, id=scan_id, user=request.user, scan_type='image')
    return render(request, 'result.html', {'scan': scan})


# ═══════════════════════════════════════════════
# VIDEO SCAN
# ═══════════════════════════════════════════════

@login_required
def upload_video_view(request):
    """Video upload and analysis."""
    form = VideoUploadForm()

    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video_file = form.cleaned_data['video']
            filename = video_file.name

            try:
                file_bytes = video_file.read()
                video_file.seek(0)

                analysis = analyze_video(file_bytes, filename=filename)

                scan = ScanResult(
                    user=request.user,
                    scan_type='video',
                    original_filename=filename,
                    authenticity_score=analysis.get('authenticity_score', 0),
                    classification=ScanResult.classify_score(analysis.get('authenticity_score', 0)),
                    real_vs_fake=analysis.get('real_vs_fake', 'Unknown'),
                    explanation=analysis.get('explanation', ''),
                    summary=analysis.get('summary', ''),
                    description=analysis.get('description', ''),
                    detailed_results=_clean_results_for_json(analysis),
                )

                scan.uploaded_file.save(filename, ContentFile(file_bytes), save=False)
                scan.save()

                profile, _ = UserProfile.objects.get_or_create(user=request.user)
                profile.increment_scans()

                messages.success(request, 'Video analysis complete!')
                return redirect('core:result_video', scan_id=scan.id)

            except Exception as e:
                logger.error(f"Video upload/analysis error: {e}", exc_info=True)
                messages.error(request, f'Analysis failed: {str(e)}')

    return render(request, 'upload_video.html', {'form': form, 'scan_type': 'video'})


@login_required
def result_video_view(request, scan_id):
    """Display video analysis results."""
    scan = get_object_or_404(ScanResult, id=scan_id, user=request.user, scan_type='video')
    return render(request, 'result_video.html', {'scan': scan})


# ═══════════════════════════════════════════════
# AUDIO SCAN
# ═══════════════════════════════════════════════

@login_required
def upload_audio_view(request):
    """Audio upload and analysis."""
    form = AudioUploadForm()

    if request.method == 'POST':
        form = AudioUploadForm(request.POST, request.FILES)
        if form.is_valid():
            audio_file = form.cleaned_data['audio']
            filename = audio_file.name

            try:
                file_bytes = audio_file.read()
                audio_file.seek(0)

                analysis = analyze_audio(file_bytes, filename=filename)

                scan = ScanResult(
                    user=request.user,
                    scan_type='audio',
                    original_filename=filename,
                    authenticity_score=analysis.get('authenticity_score', 0),
                    classification=ScanResult.classify_score(analysis.get('authenticity_score', 0)),
                    real_vs_fake=analysis.get('real_vs_fake', 'Unknown'),
                    explanation=analysis.get('explanation', ''),
                    summary=analysis.get('summary', ''),
                    description=analysis.get('description', ''),
                    detailed_results=_clean_results_for_json(analysis),
                )

                scan.uploaded_file.save(filename, ContentFile(file_bytes), save=False)
                scan.save()

                profile, _ = UserProfile.objects.get_or_create(user=request.user)
                profile.increment_scans()

                messages.success(request, 'Audio analysis complete!')
                return redirect('core:result_audio', scan_id=scan.id)

            except Exception as e:
                logger.error(f"Audio upload/analysis error: {e}", exc_info=True)
                messages.error(request, f'Analysis failed: {str(e)}')

    return render(request, 'upload_audio.html', {'form': form, 'scan_type': 'audio'})


@login_required
def result_audio_view(request, scan_id):
    """Display audio analysis results."""
    scan = get_object_or_404(ScanResult, id=scan_id, user=request.user, scan_type='audio')
    return render(request, 'result_audio.html', {'scan': scan})


# ═══════════════════════════════════════════════
# TEXT SCAN
# ═══════════════════════════════════════════════

@login_required
def text_scan_view(request):
    """Text input and analysis."""
    form = TextScanForm()

    if request.method == 'POST':
        form = TextScanForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']

            try:
                analysis = analyze_text(text)

                scan = ScanResult(
                    user=request.user,
                    scan_type='text',
                    original_filename='Text Input',
                    submitted_text=text[:5000],  # Store first 5000 chars
                    authenticity_score=analysis.get('authenticity_score', 0),
                    classification=ScanResult.classify_score(analysis.get('authenticity_score', 0)),
                    real_vs_fake=analysis.get('real_vs_fake', 'Unknown'),
                    explanation=analysis.get('explanation', ''),
                    summary=analysis.get('summary', ''),
                    description=analysis.get('description', ''),
                    detailed_results=_clean_results_for_json(analysis),
                )

                scan.save()

                profile, _ = UserProfile.objects.get_or_create(user=request.user)
                profile.increment_scans()

                messages.success(request, 'Text analysis complete!')
                return redirect('core:result_text', scan_id=scan.id)

            except Exception as e:
                logger.error(f"Text analysis error: {e}", exc_info=True)
                messages.error(request, f'Analysis failed: {str(e)}')

    return render(request, 'text_scan.html', {'form': form, 'scan_type': 'text'})


@login_required
def result_text_view(request, scan_id):
    """Display text analysis results."""
    scan = get_object_or_404(ScanResult, id=scan_id, user=request.user, scan_type='text')
    return render(request, 'result_text.html', {'scan': scan})


# ═══════════════════════════════════════════════
# PDF REPORT DOWNLOAD
# ═══════════════════════════════════════════════

@login_required
def download_report_view(request, scan_id):
    """Generate and download PDF report for a scan."""
    scan = get_object_or_404(ScanResult, id=scan_id, user=request.user)

    # Generate PDF
    pdf_bytes = generate_pdf_report(scan)

    if pdf_bytes is None:
        messages.error(request, 'PDF generation is not available. ReportLab may not be installed.')
        # Redirect back to result page
        type_map = {
            'image': 'core:result_image',
            'video': 'core:result_video',
            'audio': 'core:result_audio',
            'text': 'core:result_text',
        }
        return redirect(type_map.get(scan.scan_type, 'core:dashboard'), scan_id=scan.id)

    # Save report file to scan
    report_filename = f"DeepFakeShield_Report_{str(scan.id)[:8]}.pdf"
    if not scan.report_file:
        scan.report_file.save(report_filename, ContentFile(pdf_bytes), save=True)

    # Return PDF response
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report_filename}"'
    return response


# ═══════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════

def _clean_results_for_json(analysis_dict):
    """Remove non-JSON-serializable items from analysis results."""
    cleaned = {}
    skip_keys = {'processed_image_bytes'}

    for key, value in analysis_dict.items():
        if key in skip_keys:
            continue
        if isinstance(value, bytes):
            continue
        if isinstance(value, (int, float, str, bool, type(None))):
            cleaned[key] = value
        elif isinstance(value, (list, tuple)):
            cleaned[key] = _clean_list(value)
        elif isinstance(value, dict):
            cleaned[key] = _clean_results_for_json(value)
        else:
            try:
                cleaned[key] = str(value)
            except Exception:
                pass

    return cleaned


def _clean_list(lst):
    """Clean a list for JSON serialization."""
    cleaned = []
    for item in lst:
        if isinstance(item, (int, float, str, bool, type(None))):
            cleaned.append(item)
        elif isinstance(item, dict):
            cleaned.append(_clean_results_for_json(item))
        elif isinstance(item, (list, tuple)):
            cleaned.append(_clean_list(item))
        else:
            try:
                cleaned.append(str(item))
            except Exception:
                pass
    return cleaned