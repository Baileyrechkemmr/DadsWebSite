#!/usr/bin/env python
import os
import django
import boto3
from django.conf import settings

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'omimi.settings')
django.setup()

from projects.models import Sword_img, Sword_sales

print("=== TESTING IMAGE CONFIGURATION ===")
print(f"USE_S3: {getattr(settings, 'USE_S3', 'Not set')}")
print(f"AWS_STORAGE_BUCKET_NAME: {getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'Not set')}")
print(f"DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'Not set')}")

print("\n=== TESTING MODEL IMAGES ===")
print("Sword_img objects:")
for img in Sword_img.objects.all()[:5]:
    print(f"  Item #{img.item_number}: {img.image}")
    if img.image:
        print(f"    URL: {img.image.url}")

print("\nSword_sales objects:")
for sale in Sword_sales.objects.all()[:5]:
    if hasattr(sale, 'image') and sale.image:
        print(f"  Item #{sale.item_number}: {sale.image}")
        print(f"    URL: {sale.image.url}")

print("\n=== TESTING S3 ACCESS ===")
try:
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    
    # List objects in images/ directory
    print("Objects in 'images/' directory:")
    response = s3.list_objects_v2(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Prefix='images/', MaxKeys=10)
    if 'Contents' in response:
        for obj in response['Contents']:
            print(f"  - {obj['Key']} ({obj['Size']} bytes)")
            
            # Test access to each object
            try:
                s3.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=obj['Key'])
                print(f"    ✓ Accessible via API")
            except Exception as e:
                print(f"    ✗ API Error: {e}")
    else:
        print("  No objects found")
        
    # Check bucket policy/ACL
    print("\n=== CHECKING BUCKET CONFIGURATION ===")
    try:
        bucket_acl = s3.get_bucket_acl(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
        print("Bucket ACL found - this may cause permission issues")
        print("Grants:", len(bucket_acl.get('Grants', [])))
    except Exception as e:
        print(f"Bucket ACL check: {e}")
        
    try:
        bucket_policy = s3.get_bucket_policy(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
        print("Bucket policy exists")
    except Exception as e:
        print(f"No bucket policy found: {e}")
        
except Exception as e:
    print(f"S3 Connection Error: {e}")