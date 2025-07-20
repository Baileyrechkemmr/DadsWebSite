#!/usr/bin/env python
import os
import django
import boto3
import requests

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'omimi.settings')
django.setup()

from django.conf import settings
from projects.models import Sword_img, Sword_sales

print("=== TESTING SIGNED URL FUNCTIONALITY ===")

# Test if Django generates signed URLs when needed
s3 = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME
)

# Test a private image (from images/ folder)
private_image = Sword_sales.objects.first()
if private_image and private_image.image:
    print(f"\nTesting private image: {private_image.image}")
    print(f"Django URL: {private_image.image.url}")
    
    # Generate a signed URL manually
    signed_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': str(private_image.image)},
        ExpiresIn=3600
    )
    print(f"Manual signed URL: {signed_url[:80]}...")
    
    # Test the signed URL
    try:
        response = requests.head(signed_url, timeout=10)
        print(f"Signed URL status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Signed URLs work - private images will display correctly!")
        else:
            print("❌ Signed URL failed")
    except Exception as e:
        print(f"Error testing signed URL: {e}")

# Test a public image (from static/ folder)
public_image = Sword_img.objects.first()
if public_image and public_image.image:
    print(f"\nTesting public image: {public_image.image}")
    print(f"Django URL: {public_image.image.url}")
    
    try:
        response = requests.head(public_image.image.url, timeout=10)
        print(f"Public URL status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Public images work!")
        else:
            print("❌ Public image failed")
    except Exception as e:
        print(f"Error testing public URL: {e}")

print(f"\n=== DJANGO S3 SETTINGS ===")
print(f"AWS_QUERYSTRING_AUTH: {getattr(settings, 'AWS_QUERYSTRING_AUTH', 'Not set')}")
print(f"AWS_QUERYSTRING_EXPIRE: {getattr(settings, 'AWS_QUERYSTRING_EXPIRE', 'Not set')}")
print(f"AWS_DEFAULT_ACL: {getattr(settings, 'AWS_DEFAULT_ACL', 'Not set')}")