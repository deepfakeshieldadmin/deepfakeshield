import os
import random
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404

from .forms import (
    LoginForm, SignupForm,
    ImageUploadForm, VideoUploadForm,
    AudioUploadForm, TextScanForm
)
from .models import ScanResult, EmailVerificationToken
from .utils import get_classification, generate_explanation
from .email_utils import send_verification_email
from .report_utils import generate_pdf_report


def _generate_captcha(request):
    a = random.randint(2, 15)
    b = random.randint(1, 12)
    answer = a + b
    request.session['captcha_answer'] = answer
    request.session.modified = True
    return f"What is {a} + {b} ?"


def _verify_captcha(request, user_input):
    try:
        correct = request.session.get('captcha_answer')
        return int(str(user_input).strip()) == int(correct)
    except Exception:
        return False


def landing_view(request):
    return render(request, 'landing.html')


def home_view(request):
    return render(request, 'home.html')


def about_view(request):
    return render(request, 'about.html')


def privacy_view(request):
    return render(request, 'privacy.html')


def education_view(request):
    return render(request, 'education.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if not _verify_captcha(request, request.POST.get('captcha', '')):
            messages.error(request, 'Incorrect captcha answer.')
            captcha_question = _generate_captcha(request)
            return render(request, 'login.html', {'form': form, 'captcha_question': captcha_question})

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is None:
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None

            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.username}!')
                    return redirect('dashboard')
                messages.warning(request, 'Please verify your email before logging in.')
            else:
                messages.error(request, 'Invalid username or password.')

        captcha_question = _generate_captcha(request)
        return render(request, 'login.html', {'form': form, 'captcha_question': captcha_question})

    form = LoginForm()
    captcha_question = _generate_captcha(request)
    return render(request, 'login.html', {'form': form, 'captcha_question': captcha_question})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SignupForm(request.POST)

        if not _verify_captcha(request, request.POST.get('captcha', '')):
            messages.error(request, 'Incorrect captcha answer.')
            captcha_question = _generate_captcha(request)
            return render(request, 'signup.html', {'form': form, 'captcha_question': captcha_question})

        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']

            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered.')
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    is_active=True
                )

                token_obj = EmailVerificationToken.objects.create(user=user)
                send_verification_email(user, token_obj, request)
                messages.success(request, 'Account created successfully. Verification email sent.')
                return redirect('email_verification_sent')

        captcha_question = _generate_captcha(request)
        return render(request, 'signup.html', {'form': form, 'captcha_question': captcha_question})

    form = SignupForm()
    captcha_question = _generate_captcha(request)
    return render(request, 'signup.html', {'form': form, 'captcha_question': captcha_question})


def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')


def verify_email_view(request, token):
    try:
        token_obj = EmailVerificationToken.objects.get(token=token)
        if token_obj.is_used:
            messages.info(request, 'Email already verified.')
            return redirect('email_verification_success')

        if token_obj.is_expired():
            messages.error(request, 'Verification link expired.')
            return redirect('email_verification_failed')

        token_obj.user.is_active = True
        token_obj.user.save()
        token_obj.is_used = True
        token_obj.save()

        messages.success(request, 'Email verified successfully.')
        return redirect('email_verification_success')
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
        return redirect('email_verification_failed')


def email_verification_sent_view(request):
    return render(request, 'email_verification_sent.html')


def email_verification_success_view(request):
    return render(request, 'email_verification_success.html')


def email_verification_failed_view(request):
    return render(request, 'email_verification_failed.html')


def resend_verification_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        try:
            user = User.objects.get(email=email)
            EmailVerificationToken.objects.filter(user=user).delete()
            token_obj = EmailVerificationToken.objects.create(user=user)
            send_verification_email(user, token_obj, request)
            messages.success(request, 'Verification email sent again.')
        except User.DoesNotExist:
            messages.info(request, 'If that account exists, a verification email has been sent.')
        return redirect('login')

    return render(request, 'resend_verification.html')


@login_required
def dashboard_view(request):
    scans = ScanResult.objects.filter(user=request.user)
    context = {
        'image_count': scans.filter(scan_type='image').count(),
        'video_count': scans.filter(scan_type='video').count(),
        'audio_count': scans.filter(scan_type='audio').count(),
        'text_count': scans.filter(scan_type='text').count(),
        'recent_scans': scans[:10],
    }
    return render(request, 'dashboard.html', context)


@login_required
def upload_image_view(request):
    from .ai_engine import analyze_image, draw_face_boxes

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']

            uploads_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            processed_dir = os.path.join(settings.MEDIA_ROOT, 'processed')
            os.makedirs(uploads_dir, exist_ok=True)
            os.makedirs(processed_dir, exist_ok=True)

            file_path = os.path.join(uploads_dir, uploaded_file.name)
            with open(file_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            results, score = analyze_image(file_path)

            processed_path = os.path.join(processed_dir, f"processed_{uploaded_file.name}")
            draw_face_boxes(file_path, processed_path)

            classification = get_classification(score)
            explanation = generate_explanation('image', score, results)

            scan = ScanResult(
                user=request.user,
                scan_type='image',
                original_filename=uploaded_file.name,
                authenticity_score=score,
                classification=classification,
                explanation=explanation,
                file_size=uploaded_file.size,
            )
            scan.set_detailed_results(results)
            scan.uploaded_file = f"uploads/{uploaded_file.name}"
            if os.path.exists(processed_path):
                scan.processed_file = f"processed/processed_{uploaded_file.name}"

            scan.save()

            pdf_rel_path = generate_pdf_report(scan, results)
            if pdf_rel_path:
                scan.report_file = pdf_rel_path
                scan.save()

            return redirect('image_result', scan_id=scan.id)
    else:
        form = ImageUploadForm()

    return render(request, 'upload.html', {'form': form})


@login_required
def image_result_view(request, scan_id):
    scan = get_object_or_404(ScanResult, id=scan_id, user=request.user)
    result = scan.get_detailed_results()
    context = {
        'scan': scan,
        'result': result,
        'score_color': scan.score_color,
        'score_dashoffset': scan.score_dashoffset,
        'pdf_url': scan.report_file.url if scan.report_file else None,
    }
    return render(request, 'result.html', context)


@login_required
def upload_video_view(request):
    from .video_engine import analyze_video

    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']

            uploads_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)

            file_path = os.path.join(uploads_dir, uploaded_file.name)
            with open(file_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            results, score = analyze_video(file_path)
            classification = get_classification(score)
            explanation = generate_explanation('video', score, results)

            scan = ScanResult(
                user=request.user,
                scan_type='video',
                original_filename=uploaded_file.name,
                authenticity_score=score,
                classification=classification,
                explanation=explanation,
                file_size=uploaded_file.size,
            )
            scan.set_detailed_results(results)
            scan.uploaded_file = f"uploads/{uploaded_file.name}"
            scan.save()

            pdf_rel_path = generate_pdf_report(scan, results)
            if pdf_rel_path:
                scan.report_file = pdf_rel_path
                scan.save()

            return redirect('video_result', scan_id=scan.id)
    else:
        form = VideoUploadForm()

    return render(request, 'upload_video.html', {'form': form})


@login_required
def video_result_view(request, scan_id):
    scan = get_object_or_404(ScanResult, id=scan_id, user=request.user)
    result = scan.get_detailed_results()
    return render(request, 'result_video.html', {
        'scan': scan,
        'result': result,
        'frame_scores': result.get('frame_scores', []),
        'score_color': scan.score_color,
        'score_dashoffset': scan.score_dashoffset,
    })


@login_required
def upload_audio_view(request):
    from .audio_engine import analyze_audio

    if request.method == 'POST':
        form = AudioUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']

            uploads_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)

            file_path = os.path.join(uploads_dir, uploaded_file.name)
            with open(file_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            results, score = analyze_audio(file_path)
            classification = get_classification(score)
            explanation = generate_explanation('audio', score, results)

            scan = ScanResult(
                user=request.user,
                scan_type='audio',
                original_filename=uploaded_file.name,
                authenticity_score=score,
                classification=classification,
                explanation=explanation,
                file_size=uploaded_file.size,
            )
            scan.set_detailed_results(results)
            scan.uploaded_file = f"uploads/{uploaded_file.name}"
            scan.save()

            pdf_rel_path = generate_pdf_report(scan, results)
            if pdf_rel_path:
                scan.report_file = pdf_rel_path
                scan.save()

            return redirect('audio_result', scan_id=scan.id)
    else:
        form = AudioUploadForm()

    return render(request, 'upload_audio.html', {'form': form})


@login_required
def audio_result_view(request, scan_id):
    scan = get_object_or_404(ScanResult, id=scan_id, user=request.user)
    result = scan.get_detailed_results()
    return render(request, 'result_audio.html', {
        'scan': scan,
        'result': result,
        'score_color': scan.score_color,
        'score_dashoffset': scan.score_dashoffset,
    })


@login_required
def text_scan_view(request):
    from .text_engine import analyze_text

    if request.method == 'POST':
        form = TextScanForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            results, score = analyze_text(text)
            classification = get_classification(score)
            explanation = generate_explanation('text', score, results)

            scan = ScanResult(
                user=request.user,
                scan_type='text',
                original_filename='Text Submission',
                authenticity_score=score,
                classification=classification,
                explanation=explanation,
                submitted_text=text[:5000],
            )
            scan.set_detailed_results(results)
            scan.save()

            pdf_rel_path = generate_pdf_report(scan, results)
            if pdf_rel_path:
                scan.report_file = pdf_rel_path
                scan.save()

            return redirect('text_result', scan_id=scan.id)
    else:
        form = TextScanForm()

    return render(request, 'text_scan.html', {'form': form})


@login_required
def text_result_view(request, scan_id):
    scan = get_object_or_404(ScanResult, id=scan_id, user=request.user)
    result = scan.get_detailed_results()
    return render(request, 'result_text.html', {
        'scan': scan,
        'result': result,
        'score_color': scan.score_color,
        'score_dashoffset': scan.score_dashoffset,
    })