#!/usr/bin/env python3
"""
WSL-compatible S3 URL Debugging Tool

This simplified script helps diagnose S3 URL issues across different platforms.
It doesn't require external dependencies like 'requests'.
"""

import os
import sys
import json
import urllib.request
import urllib.error
import boto3
import environ
from pathlib import Path

# Set up colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

# Load environment variables
env = environ.Env()
environ.Env.read_env('.env')

# Get configuration
ACCESS_KEY = env('AWS_ACCESS_KEY_ID', default='')
SECRET_KEY = env('AWS_SECRET_ACCESS_KEY', default='')
REGION = env('AWS_S3_REGION', default='us-east-1')
BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', default='')
USE_S3 = env.bool('USE_S3', default=True)

# Print configuration
print(f"{Colors.BLUE}{Colors.BOLD}AWS Configuration:{Colors.END}")
print(f"AWS Access Key ID: {ACCESS_KEY[:4]}...{ACCESS_KEY[-4:] if len(ACCESS_KEY) > 8 else ''}")
print(f"Region: {REGION}")
print(f"Bucket: {BUCKET_NAME}")
print(f"USE_S3: {USE_S3}")

# Create S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION
)

# Test basic bucket access
print(f"\n{Colors.BOLD}Testing bucket access...{Colors.END}")
try:
    response = s3.head_bucket(Bucket=BUCKET_NAME)
    print(f"{Colors.GREEN}✓ Bucket exists and credentials have access{Colors.END}")
except Exception as e:
    print(f"{Colors.RED}✗ Error accessing bucket: {e}{Colors.END}")
    sys.exit(1)

# List some objects
print(f"\n{Colors.BOLD}Listing objects in 'static/' folder...{Colors.END}")
try:
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix="static/", MaxKeys=5)
    if 'Contents' in response:
        objects = response['Contents']
        for obj in objects:
            print(f"- {obj['Key']} ({obj['Size']} bytes)")
    else:
        print(f"{Colors.YELLOW}No objects found in 'static/' folder{Colors.END}")
except Exception as e:
    print(f"{Colors.RED}Error listing objects: {e}{Colors.END}")

# Function to test URL access
def test_url(url):
    try:
        # Just try to open the URL to see if it works
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req, timeout=5) as response:
            return True, response.status
    except urllib.error.HTTPError as e:
        return False, e.code
    except Exception as e:
        return False, str(e)

# Test URL formats for a key
def test_url_formats(key):
    print(f"\n{Colors.BOLD}Testing URL formats for '{key}':{Colors.END}")
    
    # Format 1: Virtual-hosted style (default in most regions)
    url1 = f"https://{BUCKET_NAME}.s3.amazonaws.com/{key}"
    success, status = test_url(url1)
    print(f"1. Virtual-hosted style: {url1}")
    if success:
        print(f"   {Colors.GREEN}✓ Works! (Status: {status}){Colors.END}")
    else:
        print(f"   {Colors.RED}✗ Failed (Status: {status}){Colors.END}")
    
    # Format 2: Virtual-hosted style with region
    url2 = f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{key}"
    success, status = test_url(url2)
    print(f"2. Virtual-hosted with region: {url2}")
    if success:
        print(f"   {Colors.GREEN}✓ Works! (Status: {status}){Colors.END}")
    else:
        print(f"   {Colors.RED}✗ Failed (Status: {status}){Colors.END}")
    
    # Format 3: Path style
    url3 = f"https://s3.{REGION}.amazonaws.com/{BUCKET_NAME}/{key}"
    success, status = test_url(url3)
    print(f"3. Path style: {url3}")
    if success:
        print(f"   {Colors.GREEN}✓ Works! (Status: {status}){Colors.END}")
    else:
        print(f"   {Colors.RED}✗ Failed (Status: {status}){Colors.END}")
    
    # Format 4: Path style without region
    url4 = f"https://s3.amazonaws.com/{BUCKET_NAME}/{key}"
    success, status = test_url(url4)
    print(f"4. Path style without region: {url4}")
    if success:
        print(f"   {Colors.GREEN}✓ Works! (Status: {status}){Colors.END}")
    else:
        print(f"   {Colors.RED}✗ Failed (Status: {status}){Colors.END}")

    return [url1, url2, url3, url4]

# Generate a Django settings fix based on which URL format worked
def generate_django_fix(working_urls):
    print(f"\n{Colors.BOLD}Recommended Django settings:{Colors.END}")
    
    # Determine which URL format works best
    if any(working_urls):
        working_index = next((i for i, url in enumerate(working_urls) if test_url(url)[0]), None)
        
        if working_index == 0 or working_index == 1:
            # Virtual-hosted style works
            print(f"{Colors.BLUE}Add to settings.py:{Colors.END}")
            print(f"""
# S3 URL Configuration
AWS_S3_ADDRESSING_STYLE = 'virtual'  # Use virtual-hosted style URLs (bucket.s3.amazonaws.com)
AWS_S3_SIGNATURE_VERSION = 's3v4'    # Use signature version 4 for better region support
""")
            
        elif working_index == 2 or working_index == 3:
            # Path style works
            print(f"{Colors.BLUE}Add to settings.py:{Colors.END}")
            print(f"""
# S3 URL Configuration
AWS_S3_ADDRESSING_STYLE = 'path'     # Use path style URLs (s3.amazonaws.com/bucket)
AWS_S3_SIGNATURE_VERSION = 's3v4'    # Use signature version 4 for better region support
""")
    else:
        print(f"{Colors.RED}No working URL format found. Check S3 bucket permissions and policies.{Colors.END}")

# Main function
def main():
    print(f"{Colors.BLUE}{Colors.BOLD}S3 URL Diagnostic Tool for WSL{Colors.END}")
    print(f"{Colors.BLUE}=============================={Colors.END}")
    
    # Get a sample object to test
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix="static/", MaxKeys=1)
        if 'Contents' in response and response['Contents']:
            key = response['Contents'][0]['Key']
            print(f"\n{Colors.BOLD}Found sample object: {key}{Colors.END}")
            
            # Test different URL formats
            working_urls = test_url_formats(key)
            
            # Generate Django settings recommendation
            generate_django_fix(working_urls)
            
        else:
            print(f"{Colors.RED}No objects found in bucket to test with{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")
        
    print(f"\n{Colors.BOLD}Next Steps:{Colors.END}")
    print("1. Update settings.py with the recommended configuration")
    print("2. Restart your Django server")
    print("3. Test image loading in your browser")

if __name__ == "__main__":
    main()