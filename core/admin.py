from django.contrib import admin
from .models import ScanResult, EmailVerificationToken


@admin.register(ScanResult)
class ScanResultAdmin(admin.ModelAdmin):
    list_display = (
        'scan_type',
        'original_filename',
        'authenticity_score',
        'classification',
        'user',
        'created_at',
    )
    list_filter = ('scan_type', 'classification', 'created_at')
    search_fields = ('original_filename', 'user__username', 'user__email')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'is_used', 'created_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('token', 'created_at')