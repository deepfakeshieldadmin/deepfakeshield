from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('home/', views.home_page, name='home'),
    path('about/', views.about_page, name='about'),
    path('privacy/', views.privacy_page, name='privacy'),
    path('education/', views.education_page, name='education'),

    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('verify-email/<str:uidb64>/<str:token>/', views.verify_email_view, name='verify_email'),
    path('resend-verification/', views.resend_verification_view, name='resend_verification'),

    path('dashboard/', views.dashboard_view, name='dashboard'),

    path('scan/image/', views.upload_image_view, name='upload_image'),
    path('scan/image/result/<uuid:scan_id>/', views.result_image_view, name='result_image'),

    path('scan/video/', views.upload_video_view, name='upload_video'),
    path('scan/video/result/<uuid:scan_id>/', views.result_video_view, name='result_video'),

    path('scan/audio/', views.upload_audio_view, name='upload_audio'),
    path('scan/audio/result/<uuid:scan_id>/', views.result_audio_view, name='result_audio'),

    path('scan/text/', views.text_scan_view, name='text_scan'),
    path('scan/text/result/<uuid:scan_id>/', views.result_text_view, name='result_text'),

    path('api/stats/', views.api_scan_stats, name='api_stats'),

    path('scan/image/report/<uuid:scan_id>/', views.download_image_report_view, name='download_image_report'),
]