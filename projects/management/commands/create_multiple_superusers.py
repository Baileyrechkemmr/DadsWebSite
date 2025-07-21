"""
Django management command to create multiple superusers from environment variables.
This supports creating multiple admin users during deployment.

Usage:
    python manage.py create_multiple_superusers

Environment variables supported:
    # Primary superuser
    DJANGO_SUPERUSER_USERNAME
    DJANGO_SUPERUSER_EMAIL  
    DJANGO_SUPERUSER_PASSWORD
    
    # Additional superusers (can add more by incrementing numbers)
    DJANGO_SUPERUSER_2_USERNAME
    DJANGO_SUPERUSER_2_EMAIL
    DJANGO_SUPERUSER_2_PASSWORD
    
    DJANGO_SUPERUSER_3_USERNAME
    DJANGO_SUPERUSER_3_EMAIL
    DJANGO_SUPERUSER_3_PASSWORD
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    help = 'Create multiple superusers from environment variables'

    def handle(self, *args, **options):
        User = get_user_model()
        created_users = []
        
        # List of possible superuser configurations
        superuser_configs = [
            {
                'username_key': 'DJANGO_SUPERUSER_USERNAME',
                'email_key': 'DJANGO_SUPERUSER_EMAIL',
                'password_key': 'DJANGO_SUPERUSER_PASSWORD',
                'label': 'Primary'
            }
        ]
        
        # Add numbered superusers (2, 3, 4, etc.)
        for i in range(2, 10):  # Support up to 9 additional superusers
            superuser_configs.append({
                'username_key': f'DJANGO_SUPERUSER_{i}_USERNAME',
                'email_key': f'DJANGO_SUPERUSER_{i}_EMAIL',
                'password_key': f'DJANGO_SUPERUSER_{i}_PASSWORD',
                'label': f'Superuser {i}'
            })
        
        # Process each configuration
        for config in superuser_configs:
            username = os.environ.get(config['username_key'])
            email = os.environ.get(config['email_key'])
            password = os.environ.get(config['password_key'])
            
            # Skip if any required variables are missing
            if not all([username, email, password]):
                if config['label'] == 'Primary':
                    self.stdout.write(
                        self.style.WARNING(
                            f'Primary superuser environment variables not set. '
                            f'Missing: {config["username_key"]}, {config["email_key"]}, or {config["password_key"]}'
                        )
                    )
                continue
            
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'{config["label"]} superuser "{username}" already exists. Skipping.')
                )
                continue
            
            # Create the superuser
            try:
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                created_users.append(username)
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created {config["label"]} superuser "{username}"')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating {config["label"]} superuser "{username}": {e}')
                )
        
        # Summary
        if created_users:
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ Created {len(created_users)} superuser(s): {", ".join(created_users)}')
            )
        else:
            self.stdout.write(
                self.style.WARNING('No new superusers were created.')
            )