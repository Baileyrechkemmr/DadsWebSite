#!/usr/bin/env python
"""
Collect static files and upload them to S3

This script runs Django's collectstatic command and ensures all static files
are properly uploaded to S3. It works across all platforms (macOS, Linux, Windows, WSL).
"""

import os
import sys
import django
from django.core.management import call_command

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'omimi.settings')
django.setup()

# Import settings after Django setup
from django.conf import settings

def check_s3_configuration():
    """Check if S3 is properly configured"""
    required_settings = [
        'AWS_ACCESS_KEY_ID', 
        'AWS_SECRET_ACCESS_KEY',
        'AWS_STORAGE_BUCKET_NAME',
        'AWS_S3_REGION_NAME',
        'STATICFILES_STORAGE'
    ]
    
    for setting in required_settings:
        if not hasattr(settings, setting) or getattr(settings, setting) in (None, ''):
            print(f"Error: {setting} is not configured properly.")
            return False
    
    if not settings.STATICFILES_STORAGE == 'storages.backends.s3boto3.S3Boto3Storage':
        print("Warning: STATICFILES_STORAGE is not set to use S3.")
        return False
        
    return True

def collect_static_files():
    """Collect static files and upload to S3"""
    # First check if S3 is properly configured
    if not check_s3_configuration():
        print("S3 configuration check failed. Please check your settings.")
        return False
    
    try:
        print("Collecting static files and uploading to S3...")
        # Call Django's collectstatic command with --no-input flag
        call_command('collectstatic', interactive=False, verbosity=2)
        print("Static files successfully collected and uploaded to S3.")
        return True
    except Exception as e:
        print(f"Error collecting static files: {e}")
        return False

if __name__ == '__main__':
    success = collect_static_files()
    sys.exit(0 if success else 1)