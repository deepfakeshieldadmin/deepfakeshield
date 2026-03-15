from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('home/', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('education/', views.education_view, name='education'),

    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    path('email/verify/<uuid:token>/', views.verify_email_view, name='verify_email'),
    path('email/sent/', views.email_verification_sent_view, name='email_verification_sent'),
    path('email/success/', views.email_verification_success_view, name='email_verification_success'),
    path('email/failed/', views.email_verification_failed_view, name='email_verification_failed'),
    path('email/resend/', views.resend_verification_view, name='resend_verification'),

    path('dashboard/', views.dashboard_view, name='dashboard'),

    path('scan/image/', views.upload_image_view, name='upload_image'),
    path('scan/image/result/<uuid:scan_id>/', views.image_result_view, name='image_result'),

    path('scan/video/', views.upload_video_view, name='upload_video'),
    path('scan/video/result/<uuid:scan_id>/', views.video_result_view, name='video_result'),

    path('scan/audio/', views.upload_audio_view, name='upload_audio'),
    path('scan/audio/result/<uuid:scan_id>/', views.audio_result_view, name='audio_result'),

    path('scan/text/', views.text_scan_view, name='text_scan'),
    path('scan/text/result/<uuid:scan_id>/', views.text_result_view, name='text_result'),
]