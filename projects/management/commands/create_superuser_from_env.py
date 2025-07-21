"""
Django management command to create a superuser from environment variables.
This is useful for deployment environments like Railway where you can't run interactive commands.

Usage:
    python manage.py create_superuser_from_env

Environment variables required:
    DJANGO_SUPERUSER_USERNAME
    DJANGO_SUPERUSER_EMAIL
    DJANGO_SUPERUSER_PASSWORD
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    help = 'Create a superuser from environment variables'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Get credentials from environment variables
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        
        # Validate that all required env vars are present
        if not all([username, email, password]):
            self.stdout.write(
                self.style.ERROR(
                    'Missing required environment variables. Please set:\n'
                    '  DJANGO_SUPERUSER_USERNAME\n'
                    '  DJANGO_SUPERUSER_EMAIL\n'
                    '  DJANGO_SUPERUSER_PASSWORD'
                )
            )
            return
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Superuser "{username}" already exists. Skipping creation.')
            )
            return
        
        # Create the superuser
        try:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created superuser "{username}"')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {e}')
            )
