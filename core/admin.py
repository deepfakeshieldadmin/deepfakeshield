"""
Admin configuration for DeepFake Shield.
"""
from django.contrib import admin
from django.utils.html import mark_safe
from .models import ScanResult, EmailVerificationToken, UserProfile


@admin.register(ScanResult)
class ScanResultAdmin(admin.ModelAdmin):
    list_display = [
        'short_id', 'user', 'scan_type', 'original_filename',
        'show_score', 'classification', 'created_at'
    ]
    list_filter = ['scan_type', 'classification', 'created_at']
    search_fields = ['user__username', 'original_filename']
    readonly_fields = ['id', 'created_at', 'updated_at']
    list_per_page = 25

    fieldsets = (
        ('Scan Info', {'fields': ('id', 'user', 'scan_type', 'original_filename')}),
        ('Files', {'fields': ('uploaded_file', 'processed_file', 'report_file', 'submitted_text')}),
        ('Analysis', {'fields': (
            'authenticity_score', 'classification', 'real_vs_fake',
            'explanation', 'summary', 'description', 'detailed_results'
        )}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def short_id(self, obj):
        return str(obj.id)[:8]
    short_id.short_description = 'ID'

    def show_score(self, obj):
        s = obj.authenticity_score
        c = '#28a745' if s >= 70 else ('#ffc107' if s >= 40 else '#dc3545')
        return mark_safe('<span style="color:%s;font-weight:bold;">%.1f%%</span>' % (c, s))
    show_score.short_description = 'Score'
    show_score.admin_order_field = 'authenticity_score'


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'is_used', 'created_at']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['token', 'created_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_email_verified', 'total_scans', 'created_at']
    list_filter = ['is_email_verified']
    search_fields = ['user__username']


admin.site.site_header = 'DeepFake Shield Admin'
admin.site.site_title = 'DeepFake Shield'
admin.site.index_title = 'System Administration'