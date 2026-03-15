"""
URL patterns for DeepFake Shield core application.
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Landing & Public Pages
    path('', views.landing_view, name='landing'),
    path('home/', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('education/', views.education_view, name='education'),

    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Email Verification
    path('verify-email/<uuid:token>/', views.verify_email_view, name='verify_email'),
    path('email-verification-sent/', views.email_verification_sent_view, name='email_verification_sent'),
    path('resend-verification/', views.resend_verification_view, name='resend_verification'),

    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Image Scan
    path('scan/image/', views.upload_image_view, name='upload_image'),
    path('result/image/<uuid:scan_id>/', views.result_image_view, name='result_image'),

    # Video Scan
    path('scan/video/', views.upload_video_view, name='upload_video'),
    path('result/video/<uuid:scan_id>/', views.result_video_view, name='result_video'),

    # Audio Scan
    path('scan/audio/', views.upload_audio_view, name='upload_audio'),
    path('result/audio/<uuid:scan_id>/', views.result_audio_view, name='result_audio'),

    # Text Scan
    path('scan/text/', views.text_scan_view, name='text_scan'),
    path('result/text/<uuid:scan_id>/', views.result_text_view, name='result_text'),

    # PDF Report Download
    path('download-report/<uuid:scan_id>/', views.download_report_view, name='download_report'),

    # API/Utility
    path('scan-history/', views.scan_history_view, name='scan_history'),
]