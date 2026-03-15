"""
Admin configuration for DeepFake Shield.
"""
from django.contrib import admin
from django.utils.html import format_html, mark_safe
from .models import ScanResult, EmailVerificationToken, UserProfile


@admin.register(ScanResult)
class ScanResultAdmin(admin.ModelAdmin):
    list_display = [
        'short_id', 'user', 'scan_type', 'original_filename',
        'get_score_display', 'classification', 'created_at'
    ]
    list_filter = ['scan_type', 'classification', 'created_at']
    search_fields = ['user__username', 'original_filename', 'explanation']
    readonly_fields = ['id', 'created_at', 'updated_at', 'get_score_html']
    list_per_page = 25
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Scan Info', {
            'fields': ('id', 'user', 'scan_type', 'original_filename')
        }),
        ('Files', {
            'fields': ('uploaded_file', 'processed_file', 'report_file', 'submitted_text')
        }),
        ('Analysis', {
            'fields': (
                'authenticity_score', 'classification', 'real_vs_fake',
                'explanation', 'summary', 'description', 'detailed_results'
            )
        }),
        ('Visual Score', {
            'fields': ('get_score_html',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='ID')
    def short_id(self, obj):
        return str(obj.id)[:8]

    @admin.display(description='Score', ordering='authenticity_score')
    def get_score_display(self, obj):
        score = obj.authenticity_score
        if score >= 75:
            color = '#28a745'
        elif score >= 40:
            color = '#ffc107'
        else:
            color = '#dc3545'
        return mark_safe(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>'.format(
                color, score
            )
        )

    @admin.display(description='Score Visual')
    def get_score_html(self, obj):
        score = obj.authenticity_score
        if score >= 75:
            color = '#28a745'
        elif score >= 40:
            color = '#ffc107'
        else:
            color = '#dc3545'
        return mark_safe(
            '<div style="background:{}; color:white; padding:8px 16px; '
            'border-radius:8px; display:inline-block; font-size:18px; '
            'font-weight:bold;">{:.1f}% — {}</div>'.format(
                color, score, obj.score_label
            )
        )


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'is_used', 'get_is_valid', 'created_at']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['token', 'created_at']

    @admin.display(description='Valid', boolean=True)
    def get_is_valid(self, obj):
        return obj.is_valid


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'is_email_verified', 'total_scans',
        'preferred_theme', 'created_at'
    ]
    list_filter = ['is_email_verified', 'preferred_theme']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at']


# Customize admin site
admin.site.site_header = 'DeepFake Shield Admin'
admin.site.site_title = 'DeepFake Shield'
admin.site.index_title = 'System Administration'