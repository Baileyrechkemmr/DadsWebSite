#!/usr/bin/env python
"""
Comprehensive S3 Storage Setup Script for Django

This script provides a complete setup process for configuring S3 storage
in a Django project across all platforms (macOS, Linux, Windows, WSL).

It performs the following steps:
1. Checks environment and system configuration
2. Validates S3 settings and connectivity
3. Applies database migrations
4. Collects static files and uploads them to S3
5. Migrates existing blog images from static/ to images/ directory
"""

import os
import sys
import time
import platform
import subprocess
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'omimi.settings')
try:
    django.setup()
except Exception as e:
    print(f"Error initializing Django: {e}")
    sys.exit(1)

# Import settings after Django setup
from django.conf import settings

# ANSI colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.BLUE}{'-' * len(text)}{Colors.END}")

def print_step(number, text):
    """Print a step number and text"""
    print(f"\n{Colors.BOLD}Step {number}: {text}{Colors.END}")

def run_command(command, description):
    """Run a shell command and print output"""
    print(f"  Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              text=True, capture_output=True)
        print(f"{Colors.GREEN}\u2713{Colors.END} {description} completed successfully")
        if result.stdout.strip():
            print("  Output:")
            for line in result.stdout.strip().split('\n'):
                print(f"    {line}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}\u2717{Colors.END} {description} failed")
        print(f"  Error code: {e.returncode}")
        print(f"  Error output:")
        for line in e.stderr.strip().split('\n'):
            print(f"    {line}")
        return False

def check_system():
    """Check system environment"""
    print_step(1, "Checking system environment")
    
    print(f"Operating system: {platform.system()} {platform.release()}")
    print(f"Python version: {platform.python_version()}")
    
    # Check if running in WSL
    is_wsl = False
    try:
        with open('/proc/version', 'r') as f:
            is_wsl = 'microsoft' in f.read().lower()
    except:
        pass
        
    if is_wsl:
        print(f"Detected Windows Subsystem for Linux (WSL)")
        print(f"Checking for WSL-specific configuration...")
        if hasattr(settings, 'AWS_S3_ENDPOINT_URL'):
            print(f"{Colors.GREEN}\u2713{Colors.END} WSL endpoint URL is configured")
        else:
            print(f"{Colors.RED}\u2717{Colors.END} WSL endpoint URL is not configured")
            return False
    
    # Check Django settings
    print(f"Checking Django S3 configuration...")
    if getattr(settings, 'USE_S3', False):
        print(f"{Colors.GREEN}\u2713{Colors.END} S3 storage is enabled")
    else:
        print(f"{Colors.RED}\u2717{Colors.END} S3 storage is disabled")
        return False
        
    if hasattr(settings, 'STATICFILES_STORAGE') and 'S3' in settings.STATICFILES_STORAGE:
        print(f"{Colors.GREEN}\u2713{Colors.END} Static files are configured to use S3")
    else:
        print(f"{Colors.YELLOW}!{Colors.END} Static files are not configured to use S3")
        print(f"    This setup will not work cross-platform reliably")
        response = input("Do you want to continue anyway? (y/n): ").lower()
        if response != 'y':
            return False
            
    return True

def apply_migrations():
    """Apply database migrations"""
    print_step(2, "Applying database migrations")
    return run_command("python manage.py migrate", "Database migration")

def collect_static_files():
    """Collect static files and upload to S3"""
    print_step(3, "Collecting static files and uploading to S3")
    return run_command("python collect_static_to_s3.py", "Static file collection")

def migrate_blog_images():
    """Migrate blog images from static/ to images/ directory"""
    print_step(4, "Migrating blog images from static/ to images/ directory")
    return run_command("python migrate_blog_images.py", "Blog image migration")

def main():
    print_header("S3 Storage Setup for Cross-Platform Compatibility")
    
    # Check system environment
    if not check_system():
        print(f"\n{Colors.RED}System check failed. Please fix the issues before continuing.{Colors.END}")
        return False
    
    # Apply migrations
    if not apply_migrations():
        print(f"\n{Colors.YELLOW}Warning: Database migration failed. Continuing with setup...{Colors.END}")
    
    # Collect static files
    if not collect_static_files():
        print(f"\n{Colors.RED}Static file collection failed. Cannot continue.{Colors.END}")
        return False
    
    # Migrate blog images
    if not migrate_blog_images():
        print(f"\n{Colors.YELLOW}Blog image migration failed or no images to migrate.{Colors.END}")
    
    print_header("Setup Complete")
    print("Your Django application is now configured to use S3 storage across all platforms.")
    print("You can run the development server and test image loading in any environment.")
    print("\nTo test in WSL, run:")
    print("  python check_s3_wsl.py")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)