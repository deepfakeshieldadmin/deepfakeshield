"""
Test email sending from command line.
Usage: python manage.py test_email recipient@example.com
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail, EmailMessage
from django.conf import settings


class Command(BaseCommand):
    help = 'Test email sending configuration'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Recipient email address')

    def handle(self, *args, **options):
        recipient = options['email']

        self.stdout.write(f"\n{'='*50}")
        self.stdout.write(f"  Email Configuration Test")
        self.stdout.write(f"{'='*50}")
        self.stdout.write(f"Backend:  {settings.EMAIL_BACKEND}")
        self.stdout.write(f"Host:     {settings.EMAIL_HOST}")
        self.stdout.write(f"Port:     {settings.EMAIL_PORT}")
        self.stdout.write(f"TLS:      {settings.EMAIL_USE_TLS}")
        self.stdout.write(f"SSL:      {getattr(settings, 'EMAIL_USE_SSL', False)}")
        self.stdout.write(f"User:     {settings.EMAIL_HOST_USER}")
        self.stdout.write(f"Password: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
        self.stdout.write(f"From:     {settings.DEFAULT_FROM_EMAIL}")
        self.stdout.write(f"To:       {recipient}")
        self.stdout.write(f"{'='*50}\n")

        try:
            email = EmailMessage(
                subject='DeepFake Shield - Email Test',
                body='<h2>Email is working!</h2><p>If you received this, email configuration is correct.</p>',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient],
            )
            email.content_subtype = 'html'
            email.send(fail_silently=False)

            self.stdout.write(self.style.SUCCESS(f'\n✅ Email sent successfully to {recipient}!'))
            self.stdout.write('Check your inbox (and spam folder).\n')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Email FAILED!'))
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            self.stdout.write(f'\nTroubleshooting:')
            self.stdout.write(f'1. Is 2-Step Verification ON for {settings.EMAIL_HOST_USER}?')
            self.stdout.write(f'2. Did you generate an App Password (not regular password)?')
            self.stdout.write(f'3. Is the App Password correct (16 chars, no spaces)?')
            self.stdout.write(f'4. Try port 465 with EMAIL_USE_SSL=True instead of TLS')
            self.stdout.write(f'5. Check Gmail security alerts at https://myaccount.google.com/security\n')