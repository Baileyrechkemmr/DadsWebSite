#!/usr/bin/env python3
"""
S3 Bucket Explorer - Diagnose and fix S3 image loading issues

This script helps troubleshoot S3 connection issues across different platforms.
It inspects the S3 bucket, lists objects, and tests URL access.
"""

import boto3
import environ
import requests
from pathlib import Path
from urllib.parse import urlparse
from botocore.exceptions import ClientError
import sys

# Set up colorful output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

# Load environment variables
env = environ.Env()
environ.Env.read_env('.env')

# Get AWS credentials
try:
    ACCESS_KEY = env('AWS_ACCESS_KEY_ID')
    SECRET_KEY = env('AWS_SECRET_ACCESS_KEY')
    REGION = env('AWS_S3_REGION', default='us-east-1')
    BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
    USE_S3 = env.bool('USE_S3', default=True)
    AWS_LOCATION = env('AWS_LOCATION', default='')
    print(f"{Colors.BLUE}{Colors.BOLD}AWS Configuration:{Colors.END}")
    print(f"AWS Access Key: {ACCESS_KEY[:4]}...{ACCESS_KEY[-4:]}")
    print(f"AWS Region: {REGION}")
    print(f"Bucket Name: {BUCKET_NAME}")
    print(f"AWS_LOCATION: '{AWS_LOCATION}'")
    print(f"USE_S3: {USE_S3}")
except Exception as e:
    print(f"{Colors.RED}Error loading AWS credentials: {e}{Colors.END}")
    sys.exit(1)

# Create S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION
)

def test_bucket_access():
    """Test basic bucket access"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}Testing Bucket Access:{Colors.END}")
    try:
        response = s3.head_bucket(Bucket=BUCKET_NAME)
        print(f"{Colors.GREEN}✓ Bucket exists and credentials have access{Colors.END}")
        return True
    except Exception as e:
        print(f"{Colors.RED}✗ Error accessing bucket: {e}{Colors.END}")
        return False

def test_bucket_policy():
    """Check the bucket policy"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}Current Bucket Policy:{Colors.END}")
    try:
        policy = s3.get_bucket_policy(Bucket=BUCKET_NAME)
        print(f"{Colors.GREEN}Policy found:{Colors.END}\n{policy['Policy']}")
    except Exception as e:
        if "NoSuchBucketPolicy" in str(e):
            print(f"{Colors.YELLOW}No bucket policy found - objects may not be publicly accessible{Colors.END}")
        else:
            print(f"{Colors.RED}Error checking bucket policy: {e}{Colors.END}")

def get_s3_objects(prefix='', max_items=15):
    """List objects in the bucket with the given prefix"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}S3 Objects in Bucket (prefix='{prefix}'):{Colors.END}")
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix, MaxKeys=max_items)
        if 'Contents' in response:
            objects = response['Contents']
            for i, obj in enumerate(objects, 1):
                print(f"{Colors.BLUE}{i}. {obj['Key']} ({obj['Size']} bytes){Colors.END}")
            print(f"Found {len(objects)} objects (showing max {max_items})")
            return objects
        else:
            print(f"{Colors.YELLOW}No objects found with prefix '{prefix}'{Colors.END}")
            return []
    except Exception as e:
        print(f"{Colors.RED}Error listing objects: {e}{Colors.END}")
        return []

def test_object_urls(objects, test_public=False):
    """Test object URLs both with signed and public access"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}Testing Object URLs:{Colors.END}")
    
    # Limit to maximum 5 objects for testing
    test_objects = objects[:5] if len(objects) > 5 else objects
    
    results = []
    
    for obj in test_objects:
        key = obj['Key']
        print(f"\n{Colors.BLUE}Testing: {key}{Colors.END}")
        
        # 1. Generate presigned URL
        try:
            presigned_url = s3.generate_presigned_url('get_object',
                Params={'Bucket': BUCKET_NAME, 'Key': key},
                ExpiresIn=3600)
            print(f"Presigned URL: {presigned_url[:60]}...{presigned_url[-20:] if len(presigned_url) > 80 else ''}")
            
            # Test presigned URL
            try:
                response = requests.head(presigned_url, timeout=5)
                if response.status_code == 200:
                    print(f"{Colors.GREEN}✓ Presigned URL works (HTTP 200){Colors.END}")
                else:
                    print(f"{Colors.RED}✗ Presigned URL returned HTTP {response.status_code}{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}✗ Error testing presigned URL: {e}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}✗ Error creating presigned URL: {e}{Colors.END}")
        
        # 2. Test direct URL (if requested)
        if test_public:
            direct_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{key}"
            print(f"Direct URL: {direct_url}")
            
            try:
                response = requests.head(direct_url, timeout=5)
                if response.status_code == 200:
                    print(f"{Colors.GREEN}✓ Direct URL works (HTTP 200){Colors.END}")
                else:
                    print(f"{Colors.RED}✗ Direct URL returned HTTP {response.status_code}{Colors.END}")
            except Exception as e:
                print(f"{Colors.RED}✗ Error testing direct URL: {e}{Colors.END}")
        
        # Test virtual-hosted style URL
        virtual_url = f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{key}"
        print(f"Virtual-hosted URL: {virtual_url}")
        
        try:
            response = requests.head(virtual_url, timeout=5)
            if response.status_code == 200:
                print(f"{Colors.GREEN}✓ Virtual-hosted URL works (HTTP 200){Colors.END}")
            else:
                print(f"{Colors.RED}✗ Virtual-hosted URL returned HTTP {response.status_code}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}✗ Error testing virtual-hosted URL: {e}{Colors.END}")
            
        # 3. Test path-style URL
        path_url = f"https://s3.{REGION}.amazonaws.com/{BUCKET_NAME}/{key}"
        print(f"Path-style URL: {path_url}")
        
        try:
            response = requests.head(path_url, timeout=5)
            if response.status_code == 200:
                print(f"{Colors.GREEN}✓ Path-style URL works (HTTP 200){Colors.END}")
            else:
                print(f"{Colors.RED}✗ Path-style URL returned HTTP {response.status_code}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}✗ Error testing path-style URL: {e}{Colors.END}")
            
    return results

def test_cors():
    """Check CORS configuration"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}CORS Configuration:{Colors.END}")
    try:
        cors = s3.get_bucket_cors(Bucket=BUCKET_NAME)
        print(f"{Colors.GREEN}CORS configuration found:{Colors.END}")
        for rule in cors.get('CORSRules', []):
            print(f"  Allowed Origins: {rule.get('AllowedOrigins', [])}")
            print(f"  Allowed Methods: {rule.get('AllowedMethods', [])}")
            print(f"  Allowed Headers: {rule.get('AllowedHeaders', [])}")
            print(f"  Max Age: {rule.get('MaxAgeSeconds', 'Not specified')}")
    except Exception as e:
        if "NoSuchCORSConfiguration" in str(e):
            print(f"{Colors.YELLOW}No CORS configuration found{Colors.END}")
        else:
            print(f"{Colors.RED}Error checking CORS: {e}{Colors.END}")

def check_django_settings():
    """Check Django settings for S3 configuration"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}Django S3 Configuration:{Colors.END}")
    
    try:
        import django
        from django.conf import settings
        django.setup()
        
        print(f"AWS_STORAGE_BUCKET_NAME: {getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'Not set')}")
        print(f"AWS_S3_REGION_NAME: {getattr(settings, 'AWS_S3_REGION_NAME', 'Not set')}")
        print(f"AWS_QUERYSTRING_AUTH: {getattr(settings, 'AWS_QUERYSTRING_AUTH', 'Not set')}")
        print(f"AWS_LOCATION: {getattr(settings, 'AWS_LOCATION', 'Not set')}")
        print(f"DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'Not set')}")
        print(f"USE_S3: {getattr(settings, 'USE_S3', 'Not set')}")
        print(f"AWS_S3_ADDRESSING_STYLE: {getattr(settings, 'AWS_S3_ADDRESSING_STYLE', 'Not set')}")
        
    except Exception as e:
        print(f"{Colors.YELLOW}Could not import Django settings: {e}{Colors.END}")

def check_image_paths():
    """Check image paths in Django models"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}Django Image Model Paths:{Colors.END}")
    
    try:
        import django
        django.setup()
        from projects.models import Sword_img
        
        images = Sword_img.objects.all()[:5]  # Get first 5 images
        if images:
            for i, image in enumerate(images, 1):
                print(f"{Colors.BLUE}{i}. {image.item_number}:{Colors.END}")
                print(f"   - image.name: {image.image.name}")
                print(f"   - image.url: {image.image.url}")
        else:
            print(f"{Colors.YELLOW}No Sword_img records found in the database{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}Error checking Django models: {e}{Colors.END}")

def main():
    print(f"\n{Colors.HEADER}{Colors.BOLD}S3 BUCKET EXPLORER{Colors.END}")
    print(f"{Colors.HEADER}==================={Colors.END}")
    
    # Check if bucket is accessible
    if not test_bucket_access():
        return
        
    # Get S3 objects in different folders
    get_s3_objects(prefix='static/', max_items=10)
    get_s3_objects(prefix='images/', max_items=5)
    
    # Check other settings
    test_bucket_policy()
    test_cors()
    
    # Test specific objects
    static_objects = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix='static/', MaxKeys=3).get('Contents', [])
    if static_objects:
        test_object_urls(static_objects, test_public=True)
    
    # Check Django settings and models
    check_django_settings()
    check_image_paths()
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}Testing complete.{Colors.END}")
    
    # Print recommendations
    print(f"\n{Colors.HEADER}{Colors.BOLD}RECOMMENDATIONS:{Colors.END}")
    print(f"1. Make sure AWS_S3_ADDRESSING_STYLE is set to 'virtual' in Django settings")
    print(f"2. Ensure CORS configuration allows access from your domain")
    print(f"3. Check that the bucket policy allows public read access to your image paths")
    print(f"4. Verify the URLs being generated match the actual S3 object paths")
    

if __name__ == "__main__":
    main()