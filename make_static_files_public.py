#!/usr/bin/env python
"""
Script to make all static files in S3 bucket publicly readable.
This fixes the 403 Forbidden errors on pre-signed URLs by making the files publicly accessible.
"""
import os
import sys
import django
import boto3
from botocore.exceptions import ClientError

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'omimi.settings')
django.setup()

from django.conf import settings


def make_static_files_public():
    """Update ACL for all static files to public-read"""
    
    # Create S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    prefix = 'static/'
    
    print(f"Making static files public in bucket: {bucket_name}")
    print(f"Processing files with prefix: {prefix}")
    print("-" * 50)
    
    # List all objects in the static folder
    paginator = s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
    
    updated_count = 0
    error_count = 0
    
    for page in pages:
        if 'Contents' not in page:
            continue
            
        for obj in page['Contents']:
            key = obj['Key']
            
            try:
                # Update ACL to public-read
                s3_client.put_object_acl(
                    Bucket=bucket_name,
                    Key=key,
                    ACL='public-read'
                )
                print(f"✓ Updated: {key}")
                updated_count += 1
                
            except ClientError as e:
                print(f"✗ Error updating {key}: {e}")
                error_count += 1
    
    print("-" * 50)
    print(f"Summary: {updated_count} files updated, {error_count} errors")
    
    # Test a file to make sure it's accessible
    if updated_count > 0:
        test_file = 'static/howard1.jpeg'
        public_url = f"https://{bucket_name}.s3.amazonaws.com/{test_file}"
        print(f"\nTest URL (should be publicly accessible):")
        print(f"  {public_url}")
        
        print("\nAlternatively, you can add a bucket policy to make all static files public:")
        print(f"""
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadStaticFiles",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::{bucket_name}/static/*"
        }
    ]
}
        """)
        print("This bucket policy can be added via AWS Console > S3 > Bucket > Permissions > Bucket Policy")


if __name__ == '__main__':
    try:
        make_static_files_public()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)