"""
═══════════════════════════════════════════════════════════
DEEP FAKE SHIELD — ADMIN PANEL CONFIGURATION

This file registers all models with Django's admin interface
so teachers and administrators can:
  - View all registered users
  - See all uploaded images and scan results
  - Review detection results
  - View scan history
  - Manage email verification status
═══════════════════════════════════════════════════════════
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import ImageScan, VideoScan, AudioScan, TextScan, UserProfile, EmailVerification


# ═══════════════════════════════════════════════════════════
# CUSTOM ADMIN SITE BRANDING
# ═══════════════════════════════════════════════════════════
admin.site.site_header = "🛡️ Deep Fake Shield — Admin Panel"
admin.site.site_title = "DeepFakeShield Admin"
admin.site.index_title = "Welcome to Deep Fake Shield Administration"


# ═══════════════════════════════════════════════════════════
# IMAGE SCAN ADMIN
# ═══════════════════════════════════════════════════════════
@admin.register(ImageScan)
class ImageScanAdmin(admin.ModelAdmin):
    """Admin view for image scan results."""

    list_display = (
        'original_filename',
        'user',
        'colored_score',
        'classification_badge',
        'face_count',
        'has_exif',
        'is_ai_generated',
        'created_at',
    )

    list_filter = (
        'classification',
        'has_exif',
        'is_ai_generated',
        'is_edited',
        'created_at',
    )

    search_fields = (
        'original_filename',
        'user__username',
        'user__email',
    )

    readonly_fields = ('id', 'created_at', 'image_preview')
    ordering = ('-created_at',)

    fieldsets = (
        ('📋 Basic Info', {
            'fields': ('id', 'user', 'image', 'image_preview', 'original_filename')
        }),
        ('📊 Analysis Results', {
            'fields': ('authenticity_score', 'classification', 'is_ai_generated', 'is_edited')
        }),
        ('👤 Face Detection', {
            'fields': ('face_count',)
        }),
        ('📷 Metadata', {
            'fields': ('has_exif', 'exif_data')
        }),
        ('📝 Details', {
            'fields': ('analysis_details', 'explanation'),
            'classes': ('collapse',)
        }),
        ('📅 Timestamps', {
            'fields': ('created_at',)
        }),
    )

    def colored_score(self, obj):
        """Display score with color coding."""
        score = obj.authenticity_score
        if score >= 90:
            color = '#28a745'
        elif score >= 75:
            color = '#17a2b8'
        elif score >= 40:
            color = '#ffc107'
        else:
            color = '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold; font-size: 14px;">{:.1f}%</span>',
            color, score
        )
    colored_score.short_description = 'Score'
    colored_score.admin_order_field = 'authenticity_score'

    def classification_badge(self, obj):
        """Display classification as a colored badge."""
        colors = {
            'authentic': ('#28a745', '✅ Authentic'),
            'likely_real': ('#17a2b8', '✅ Likely Real'),
            'suspicious': ('#ffc107', '⚠️ Suspicious'),
            'likely_fake': ('#dc3545', '❌ Likely Fake'),
        }
        color, label = colors.get(obj.classification, ('#6c757d', '❓ Unknown'))
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color, label
        )
    classification_badge.short_description = 'Classification'

    def image_preview(self, obj):
        """Show small preview of the uploaded image."""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; '
                'border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'


# ═══════════════════════════════════════════════════════════
# VIDEO SCAN ADMIN
# ═══════════════════════════════════════════════════════════
@admin.register(VideoScan)
class VideoScanAdmin(admin.ModelAdmin):
    list_display = (
        'original_filename',
        'user',
        'colored_score',
        'classification',
        'total_frames_analyzed',
        'created_at',
    )
    list_filter = ('classification', 'created_at')
    search_fields = ('original_filename', 'user__username')
    readonly_fields = ('id', 'created_at')
    ordering = ('-created_at',)

    def colored_score(self, obj):
        score = obj.authenticity_score
        if score >= 90: color = '#28a745'
        elif score >= 75: color = '#17a2b8'
        elif score >= 40: color = '#ffc107'
        else: color = '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, score
        )
    colored_score.short_description = 'Score'


# ═══════════════════════════════════════════════════════════
# AUDIO SCAN ADMIN
# ═══════════════════════════════════════════════════════════
@admin.register(AudioScan)
class AudioScanAdmin(admin.ModelAdmin):
    list_display = (
        'original_filename',
        'user',
        'colored_score',
        'classification',
        'duration_seconds',
        'created_at',
    )
    list_filter = ('classification', 'created_at')
    search_fields = ('original_filename', 'user__username')
    readonly_fields = ('id', 'created_at')
    ordering = ('-created_at',)

    def colored_score(self, obj):
        score = obj.authenticity_score
        if score >= 90: color = '#28a745'
        elif score >= 75: color = '#17a2b8'
        elif score >= 40: color = '#ffc107'
        else: color = '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, score
        )
    colored_score.short_description = 'Score'


# ═══════════════════════════════════════════════════════════
# TEXT SCAN ADMIN
# ═══════════════════════════════════════════════════════════
@admin.register(TextScan)
class TextScanAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'word_count',
        'colored_score',
        'classification',
        'text_preview',
        'created_at',
    )
    list_filter = ('classification', 'created_at')
    search_fields = ('user__username', 'input_text')
    readonly_fields = ('id', 'created_at')
    ordering = ('-created_at',)

    def colored_score(self, obj):
        score = obj.authenticity_score
        if score >= 90: color = '#28a745'
        elif score >= 75: color = '#17a2b8'
        elif score >= 40: color = '#ffc107'
        else: color = '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, score
        )
    colored_score.short_description = 'Score'

    def text_preview(self, obj):
        """Show first 80 characters of text."""
        text = obj.input_text[:80]
        if len(obj.input_text) > 80:
            text += '...'
        return text
    text_preview.short_description = 'Text Preview'


# ═══════════════════════════════════════════════════════════
# USER PROFILE ADMIN
# ═══════════════════════════════════════════════════════════
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'theme',
        'language',
        'dark_mode',
        'total_scans',
        'created_at',
    )
    list_filter = ('theme', 'language', 'dark_mode')
    search_fields = ('user__username', 'user__email')
    ordering = ('-created_at',)


# ═══════════════════════════════════════════════════════════
# EMAIL VERIFICATION ADMIN
# ═══════════════════════════════════════════════════════════
@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'user_email',
        'verification_status',
        'verification_sent_at',
        'verified_at',
    )
    list_filter = ('is_verified',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('verification_sent_at', 'verified_at')

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

    def verification_status(self, obj):
        if obj.is_verified:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 12px; font-size: 11px;">✅ Verified</span>'
            )
        else:
            return format_html(
                '<span style="background: #ffc107; color: #333; padding: 3px 10px; '
                'border-radius: 12px; font-size: 11px;">⏳ Pending</span>'
            )
    verification_status.short_description = 'Status'