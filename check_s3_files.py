#!/usr/bin/env python3
"""
Check what files actually exist in S3 bucket
"""

import boto3
import os

def check_specific_files():
    # AWS Configuration
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME', 'ominisword-images')
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    region = os.environ.get('AWS_S3_REGION', 'us-east-1')
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=region
    )
    
    print("🔍 Checking specific files in S3...")
    
    # Files we're trying to access
    test_files = [
        'images/sword_one.webp',
        'static/blog.png', 
        'images/100_3589.png'
    ]
    
    for file_path in test_files:
        try:
            response = s3_client.head_object(Bucket=bucket_name, Key=file_path)
            size_kb = response['ContentLength'] / 1024
            print(f"✅ {file_path} EXISTS ({size_kb:.1f} KB)")
            
            # Try to generate a presigned URL
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': file_path},
                ExpiresIn=3600
            )
            print(f"   Presigned URL: {url[:100]}...")
            
        except Exception as e:
            print(f"❌ {file_path} NOT FOUND: {e}")
    
    # Also check what's actually in the images/ directory
    print(f"\n📁 Contents of 'images/' directory:")
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix='images/')
        if 'Contents' in response:
            for obj in response['Contents'][:10]:
                size_kb = obj['Size'] / 1024
                print(f"   • {obj['Key']} ({size_kb:.1f} KB)")
        else:
            print("   No files found in images/ directory")
    except Exception as e:
        print(f"   Error listing images/: {e}")

if __name__ == "__main__":
    check_specific_files()