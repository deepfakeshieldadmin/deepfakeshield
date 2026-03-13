"""
Views for DeepFakeShield.
Handles pages, authentication, dashboard, scans, and compulsory email verification.
"""
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.utils import timezone
from django.http import FileResponse
from .report_utils import build_image_scan_pdf

from .forms import (
    SignUpForm,
    LoginForm,
    ImageUploadForm,
    VideoUploadForm,
    AudioUploadForm,
    TextAnalysisForm,
    generate_captcha,
)
from .models import ImageScan, VideoScan, AudioScan, TextScan, UserProfile, EmailVerification
from .ai_engine import analyze_image
from .video_engine import analyze_video
from .audio_engine import analyze_audio
from .text_engine import analyze_text
from .tokens import email_verification_token
from .email_utils import send_verification_email, is_valid_email


# ═══════════════════════════════════════
# PUBLIC PAGES
# ═══════════════════════════════════════

def landing_page(request):
    return render(request, "landing.html")


def home_page(request):
    return render(request, "home.html")


def about_page(request):
    return render(request, "about.html")


def privacy_page(request):
    return render(request, "privacy.html")


def education_page(request):
    return render(request, "education.html")


# ═══════════════════════════════════════
# AUTHENTICATION
# ═══════════════════════════════════════

def signup_view(request):
    """
    Signup with compulsory email verification.
    User is created inactive.
    Verification mail is sent.
    Account becomes active only after clicking verification link.
    """
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        captcha_correct = request.session.get("captcha_answer", "")
        form = SignUpForm(
            request.POST,
            captcha_question=request.session.get("captcha_question", ""),
            captcha_correct=captcha_correct,
        )

        if form.is_valid():
            email = form.cleaned_data.get("email", "").strip().lower()

            if not is_valid_email(email):
                messages.error(request, "No valid email detected. Please enter a valid email.")
                question, answer = generate_captcha()
                request.session["captcha_question"] = question
                request.session["captcha_answer"] = answer
                return render(request, "signup.html", {
                    "form": form,
                    "captcha_question": request.session.get("captcha_question", ""),
                })

            user = form.save(commit=False)
            user.email = email
            user.is_active = False
            user.save()

            UserProfile.objects.get_or_create(user=user)
            EmailVerification.objects.get_or_create(user=user)

            email_sent = send_verification_email(request, user)

            if email_sent:
                messages.success(
                    request,
                    f"Verification email sent to {email}. Please open your inbox and click the verification link."
                )
                return render(request, "email_verification_sent.html", {
                    "email": email,
                    "user_obj": user,
                })
            else:
                user.delete()
                messages.error(
                    request,
                    "Could not send verification email. Please try again with a valid email."
                )
        else:
            messages.error(request, "Please correct the form errors below.")

        question, answer = generate_captcha()
        request.session["captcha_question"] = question
        request.session["captcha_answer"] = answer

    else:
        form = SignUpForm(captcha_question="", captcha_correct="")
        question, answer = generate_captcha()
        request.session["captcha_question"] = question
        request.session["captcha_answer"] = answer

    return render(request, "signup.html", {
        "form": form,
        "captcha_question": request.session.get("captcha_question", ""),
    })


def login_view(request):
    """
    Login only for verified and active users.
    """
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            if not user.is_active:
                messages.warning(
                    request,
                    "Your account is not verified yet. Please verify your email before logging in."
                )
                return redirect("resend_verification")

            login(request, user)
            UserProfile.objects.get_or_create(user=user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect("home")


def verify_email_view(request, uidb64, token):
    """
    User clicks the link from email.
    Account becomes active and verified.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and email_verification_token.check_token(user, token):
        user.is_active = True
        user.save()

        verification, _ = EmailVerification.objects.get_or_create(user=user)
        verification.is_verified = True
        verification.verified_at = timezone.now()
        verification.save()

        login(request, user)
        messages.success(request, "Email verified successfully. Your account is now active.")
        return redirect("dashboard")

    messages.error(request, "Verification link is invalid or expired.")
    return render(request, "email_verification_failed.html")


def resend_verification_view(request):
    """
    Resend verification email to unverified users.
    """
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()

        if not email:
            messages.error(request, "Please enter your email address.")
            return render(request, "resend_verification.html")

        if not is_valid_email(email):
            messages.error(request, "No valid email detected. Please enter a valid email.")
            return render(request, "resend_verification.html")

        try:
            user = User.objects.get(email__iexact=email)

            if user.is_active:
                messages.info(request, "This account is already verified. Please login.")
                return redirect("login")

            sent = send_verification_email(request, user)
            if sent:
                messages.success(request, f"Verification email sent again to {email}.")
            else:
                messages.error(request, "Could not send verification email. Please try again.")
        except User.DoesNotExist:
            messages.error(request, "No account found with that email address.")

    return render(request, "resend_verification.html")


# ═══════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════

@login_required
def dashboard_view(request):
    user = request.user

    image_count = ImageScan.objects.filter(user=user).count()
    video_count = VideoScan.objects.filter(user=user).count()
    audio_count = AudioScan.objects.filter(user=user).count()
    text_count = TextScan.objects.filter(user=user).count()
    total_scans = image_count + video_count + audio_count + text_count

    recent_images = ImageScan.objects.filter(user=user).order_by("-created_at")[:5]
    recent_videos = VideoScan.objects.filter(user=user).order_by("-created_at")[:5]
    recent_audios = AudioScan.objects.filter(user=user).order_by("-created_at")[:5]
    recent_texts = TextScan.objects.filter(user=user).order_by("-created_at")[:5]

    threats_detected = (
        ImageScan.objects.filter(user=user, classification__in=["suspicious", "likely_fake"]).count()
        + VideoScan.objects.filter(user=user, classification__in=["suspicious", "likely_fake"]).count()
        + AudioScan.objects.filter(user=user, classification__in=["suspicious", "likely_fake"]).count()
        + TextScan.objects.filter(user=user, classification__in=["suspicious", "likely_fake"]).count()
    )

    return render(request, "dashboard.html", {
        "image_count": image_count,
        "video_count": video_count,
        "audio_count": audio_count,
        "text_count": text_count,
        "total_scans": total_scans,
        "threats_detected": threats_detected,
        "recent_images": recent_images,
        "recent_videos": recent_videos,
        "recent_audios": recent_audios,
        "recent_texts": recent_texts,
    })


# ═══════════════════════════════════════
# IMAGE SCAN
# ═══════════════════════════════════════

@login_required
def upload_image_view(request):
    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = form.cleaned_data["image"]
            original_filename = image_file.name

            scan = ImageScan(
                user=request.user,
                image=image_file,
                original_filename=original_filename,
            )
            scan.save()

            try:
                result = analyze_image(scan.image.path)

                scan.authenticity_score = result.get("authenticity_score", 0.0)
                scan.classification = result.get("classification", "suspicious")
                scan.is_ai_generated = result.get("is_ai_generated", False)
                scan.is_edited = result.get("is_edited", False)
                scan.face_count = int(result.get("face_count", 0))
                scan.has_exif = result.get("has_exif", False)
                scan.exif_data = result.get("exif_data", {})
                scan.analysis_details = result.get("details", {})
                scan.explanation = result.get("explanation", "")

                try:
                    from .ai_engine import generate_face_detection_image
                    face_img_path, _, face_locations = generate_face_detection_image(scan.image.path)
                    if face_img_path:
                        relative_path = os.path.relpath(face_img_path, settings.MEDIA_ROOT)
                        scan.analysis_details["face_detection_image"] = relative_path
                        scan.analysis_details["face_locations"] = face_locations
                except Exception:
                    pass

                scan.save()

                profile, _ = UserProfile.objects.get_or_create(user=request.user)
                profile.total_scans += 1
                profile.save()

                return redirect("result_image", scan_id=scan.id)

            except Exception as e:
                messages.error(request, f"Image analysis failed: {str(e)}")
                scan.delete()
        else:
            messages.error(request, "Please select a valid image file.")
    else:
        form = ImageUploadForm()

    return render(request, "upload.html", {"form": form})


@login_required
def result_image_view(request, scan_id):
    scan = get_object_or_404(ImageScan, id=scan_id, user=request.user)
    return render(request, "result.html", {"scan": scan})


# ═══════════════════════════════════════
# VIDEO SCAN
# ═══════════════════════════════════════

@login_required
def upload_video_view(request):
    if request.method == "POST":
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video_file = form.cleaned_data["video"]
            original_filename = video_file.name

            scan = VideoScan(
                user=request.user,
                video=video_file,
                original_filename=original_filename,
            )
            scan.save()

            try:
                result = analyze_video(scan.video.path)

                scan.authenticity_score = result.get("authenticity_score", 0.0)
                scan.classification = result.get("classification", "suspicious")
                scan.total_frames_analyzed = result.get("total_frames_analyzed", 0)
                scan.frame_scores = result.get("frame_scores", [])
                scan.analysis_details = result.get("details", {})
                scan.explanation = result.get("explanation", "")
                scan.save()

                profile, _ = UserProfile.objects.get_or_create(user=request.user)
                profile.total_scans += 1
                profile.save()

                return redirect("result_video", scan_id=scan.id)

            except Exception as e:
                messages.error(request, f"Video analysis failed: {str(e)}")
                scan.delete()
        else:
            messages.error(request, "Please select a valid video file.")
    else:
        form = VideoUploadForm()

    return render(request, "upload_video.html", {"form": form})


@login_required
def result_video_view(request, scan_id):
    scan = get_object_or_404(VideoScan, id=scan_id, user=request.user)
    return render(request, "result_video.html", {"scan": scan})


# ═══════════════════════════════════════
# AUDIO SCAN
# ═══════════════════════════════════════

@login_required
def upload_audio_view(request):
    if request.method == "POST":
        form = AudioUploadForm(request.POST, request.FILES)
        if form.is_valid():
            audio_file = form.cleaned_data["audio"]
            original_filename = audio_file.name

            scan = AudioScan(
                user=request.user,
                audio=audio_file,
                original_filename=original_filename,
            )
            scan.save()

            try:
                result = analyze_audio(scan.audio.path)

                scan.authenticity_score = result.get("authenticity_score", 0.0)
                scan.classification = result.get("classification", "suspicious")
                scan.duration_seconds = result.get("duration_seconds", 0.0)
                scan.analysis_details = result.get("details", {})
                scan.explanation = result.get("explanation", "")
                scan.save()

                profile, _ = UserProfile.objects.get_or_create(user=request.user)
                profile.total_scans += 1
                profile.save()

                return redirect("result_audio", scan_id=scan.id)

            except Exception as e:
                messages.error(request, f"Audio analysis failed: {str(e)}")
                scan.delete()
        else:
            messages.error(request, "Please select a valid audio file.")
    else:
        form = AudioUploadForm()

    return render(request, "upload_audio.html", {"form": form})


@login_required
def result_audio_view(request, scan_id):
    scan = get_object_or_404(AudioScan, id=scan_id, user=request.user)
    return render(request, "result_audio.html", {"scan": scan})


# ═══════════════════════════════════════
# TEXT SCAN
# ═══════════════════════════════════════

@login_required
def text_scan_view(request):
    if request.method == "POST":
        form = TextAnalysisForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data["text"]

            try:
                result = analyze_text(text)

                scan = TextScan(
                    user=request.user,
                    input_text=text,
                    word_count=len(text.split()),
                    authenticity_score=result.get("authenticity_score", 0.0),
                    classification=result.get("classification", "suspicious"),
                    analysis_details=result.get("details", {}),
                    explanation=result.get("explanation", ""),
                )
                scan.save()

                profile, _ = UserProfile.objects.get_or_create(user=request.user)
                profile.total_scans += 1
                profile.save()

                return redirect("result_text", scan_id=scan.id)

            except Exception as e:
                messages.error(request, f"Text analysis failed: {str(e)}")
        else:
            messages.error(request, "Please enter valid text.")
    else:
        form = TextAnalysisForm()

    return render(request, "text_scan.html", {"form": form})


@login_required
def result_text_view(request, scan_id):
    scan = get_object_or_404(TextScan, id=scan_id, user=request.user)
    return render(request, "result_text.html", {"scan": scan})


# ═══════════════════════════════════════
# SIMPLE API
# ═══════════════════════════════════════

@login_required
def api_scan_stats(request):
    user = request.user
    return JsonResponse({
        "images": ImageScan.objects.filter(user=user).count(),
        "videos": VideoScan.objects.filter(user=user).count(),
        "audios": AudioScan.objects.filter(user=user).count(),
        "texts": TextScan.objects.filter(user=user).count(),
    })

@login_required
def download_image_report_view(request, scan_id):
    scan = get_object_or_404(ImageScan, id=scan_id, user=request.user)
    pdf_buffer = build_image_scan_pdf(scan)
    filename = f"deepfakeshield_report_{scan.id}.pdf"
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename)