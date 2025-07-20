#!/usr/bin/env python
"""
WSL-specific S3 configuration check

This script checks if your S3 configuration will work properly in the WSL environment.
It validates settings, checks network connectivity, and tests S3 URLs using different formats.
"""

import os
import sys
import platform
import socket
import urllib.request
import urllib.error
import boto3
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'omimi.settings')
django.setup()

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

def is_wsl():
    """Check if we're running in WSL"""
    try:
        with open('/proc/version', 'r') as f:
            if 'microsoft' in f.read().lower():
                return True
    except:
        pass
        
    return False

def check_environment():
    """Check environment details"""
    print(f"{Colors.BOLD}System Information:{Colors.END}")
    print(f"Platform: {platform.platform()}")
    print(f"Python version: {platform.python_version()}")
    print(f"Running in WSL: {'Yes' if is_wsl() else 'No'}")
    
    if not is_wsl():
        print(f"\n{Colors.YELLOW}Warning: This script is designed to check WSL-specific issues,")
        print(f"but you don't appear to be running in WSL.{Colors.END}")

def check_s3_configuration():
    """Check S3-related Django settings"""
    print(f"\n{Colors.BOLD}S3 Configuration Check:{Colors.END}")
    
    # Check required settings
    required_settings = {
        'AWS_ACCESS_KEY_ID': 'Access key for S3',
        'AWS_SECRET_ACCESS_KEY': 'Secret key for S3',
        'AWS_STORAGE_BUCKET_NAME': 'S3 bucket name',
        'AWS_S3_REGION_NAME': 'S3 region',
        'USE_S3': 'Flag to use S3 storage',
        'DEFAULT_FILE_STORAGE': 'Django storage backend',
    }
    
    for setting, description in required_settings.items():
        if hasattr(settings, setting):
            value = getattr(settings, setting)
            if setting.endswith('KEY'):
                # Mask sensitive values
                masked = f"{value[:4]}...{value[-4:]}" if value and len(value) > 8 else "[Not set]"
                print(f"{Colors.GREEN}✓{Colors.END} {setting}: {masked}")
            elif setting == 'USE_S3':
                if value:
                    print(f"{Colors.GREEN}✓{Colors.END} {setting}: {value}")
                else:
                    print(f"{Colors.RED}✗{Colors.END} {setting}: {value} - S3 storage is disabled")
            elif setting == 'DEFAULT_FILE_STORAGE' and 'S3' in value:
                print(f"{Colors.GREEN}✓{Colors.END} {setting}: {value}")
            elif setting != 'DEFAULT_FILE_STORAGE':
                print(f"{Colors.GREEN}✓{Colors.END} {setting}: {value}")
            else:
                print(f"{Colors.YELLOW}!{Colors.END} {setting}: {value}")
        else:
            print(f"{Colors.RED}✗{Colors.END} {setting}: Not configured - {description}")
    
    # Check WSL-specific settings
    print(f"\n{Colors.BOLD}WSL-Specific Settings:{Colors.END}")
    if hasattr(settings, 'AWS_S3_ENDPOINT_URL'):
        print(f"{Colors.GREEN}✓{Colors.END} AWS_S3_ENDPOINT_URL: {settings.AWS_S3_ENDPOINT_URL}")
    else:
        print(f"{Colors.RED}✗{Colors.END} AWS_S3_ENDPOINT_URL: Not set - This is recommended for WSL")
    
    # Check STATICFILES_STORAGE
    if hasattr(settings, 'STATICFILES_STORAGE'):
        if 'S3' in settings.STATICFILES_STORAGE:
            print(f"{Colors.GREEN}✓{Colors.END} STATICFILES_STORAGE: {settings.STATICFILES_STORAGE}")
        else:
            print(f"{Colors.YELLOW}!{Colors.END} STATICFILES_STORAGE: {settings.STATICFILES_STORAGE} - Not using S3")
    else:
        print(f"{Colors.YELLOW}!{Colors.END} STATICFILES_STORAGE: Not configured - Using default local storage")

def check_s3_connectivity():
    """Check if we can connect to S3"""
    print(f"\n{Colors.BOLD}S3 Connectivity Test:{Colors.END}")
    try:
        # Create S3 client
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            endpoint_url=getattr(settings, 'AWS_S3_ENDPOINT_URL', None)
        )
        
        # Test bucket access
        s3.head_bucket(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
        print(f"{Colors.GREEN}✓{Colors.END} Successfully connected to bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
        
        # List a few objects
        try:
            response = s3.list_objects_v2(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                MaxKeys=3
            )
            if 'Contents' in response:
                print(f"{Colors.GREEN}✓{Colors.END} Found {len(response['Contents'])} objects in bucket")
                for i, obj in enumerate(response['Contents']):
                    print(f"  {i+1}. {obj['Key']} ({obj['Size']} bytes)")
                return True
            else:
                print(f"{Colors.YELLOW}!{Colors.END} Bucket is empty")
                return True
        except Exception as e:
            print(f"{Colors.RED}✗{Colors.END} Error listing objects: {e}")
            return False
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.END} Failed to connect to S3: {e}")
        return False

def test_url_access(url):
    """Test if a URL is accessible"""
    try:
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req, timeout=5) as response:
            return True, response.status
    except urllib.error.HTTPError as e:
        return False, e.code
    except Exception as e:
        return False, str(e)

def test_s3_url_styles():
    """Test different S3 URL styles"""
    print(f"\n{Colors.BOLD}Testing S3 URL Styles:{Colors.END}")
    
    # Get a sample object from the bucket
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            endpoint_url=getattr(settings, 'AWS_S3_ENDPOINT_URL', None)
        )
        
        response = s3.list_objects_v2(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            MaxKeys=1
        )
        
        if 'Contents' not in response or not response['Contents']:
            print(f"{Colors.YELLOW}!{Colors.END} No objects found in bucket to test URL styles")
            return
            
        test_key = response['Contents'][0]['Key']
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        region = settings.AWS_S3_REGION_NAME
        
        print(f"Testing URL access for object: {test_key}")
        
        # Test different URL styles
        url_styles = [
            ("Virtual-hosted style", f"https://{bucket_name}.s3.amazonaws.com/{test_key}"),
            ("Virtual-hosted with region", f"https://{bucket_name}.s3.{region}.amazonaws.com/{test_key}"),
            ("Path style with region", f"https://s3.{region}.amazonaws.com/{bucket_name}/{test_key}"),
            ("Path style without region", f"https://s3.amazonaws.com/{bucket_name}/{test_key}")
        ]
        
        for style_name, url in url_styles:
            success, status = test_url_access(url)
            if success:
                print(f"{Colors.GREEN}✓{Colors.END} {style_name}: {url}")
            else:
                print(f"{Colors.RED}✗{Colors.END} {style_name}: {url} (Status: {status})")
                
        # Generate recommendation
        print(f"\n{Colors.BOLD}Recommended settings based on URL tests:{Colors.END}")
        if test_url_access(url_styles[0][1])[0] or test_url_access(url_styles[1][1])[0]:
            print("AWS_S3_ADDRESSING_STYLE = 'virtual'  # bucket.s3.amazonaws.com/key")
        else:
            print("AWS_S3_ADDRESSING_STYLE = 'path'     # s3.amazonaws.com/bucket/key")
        print("AWS_S3_SIGNATURE_VERSION = 's3v4'")
        print("AWS_S3_ENDPOINT_URL = 'https://s3.amazonaws.com'  # For WSL compatibility")
            
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.END} Error testing S3 URLs: {e}")

def main():
    print(f"{Colors.BLUE}{Colors.BOLD}WSL S3 Configuration Check{Colors.END}")
    print(f"{Colors.BLUE}=========================={Colors.END}\n")
    
    check_environment()
    check_s3_configuration()
    connectivity_ok = check_s3_connectivity()
    
    if connectivity_ok:
        test_s3_url_styles()
        
    print(f"\n{Colors.BOLD}Check complete!{Colors.END}")

if __name__ == '__main__':
    main()