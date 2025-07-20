#!/usr/bin/env python
"""
Migrate BlogImages from static/ to images/ directory in S3

This script helps migrate existing BlogImages that were uploaded to 'static/' directory
to the new 'images/' directory in S3. It should be run after applying the model migration.

Enhanced with better error handling and diagnostic information.
"""

import os
import sys
import time
import boto3
import django
from django.conf import settings
from botocore.exceptions import ClientError

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'omimi.settings')
django.setup()

from projects.models import BlogImages

def check_s3_configuration():
    """Check if S3 is properly configured"""
    required_settings = [
        'AWS_ACCESS_KEY_ID', 
        'AWS_SECRET_ACCESS_KEY',
        'AWS_STORAGE_BUCKET_NAME',
        'AWS_S3_REGION_NAME'
    ]
    
    for setting in required_settings:
        if not hasattr(settings, setting) or getattr(settings, setting) in (None, ''):
            print(f"Error: {setting} is not configured properly.")
            return False
    
    return True

def verify_s3_access(s3_client, bucket_name):
    """Verify that we can access the S3 bucket"""
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✓ Successfully connected to S3 bucket: {bucket_name}")
        return True
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code')
        if error_code == '403':
            print(f"⨯ Permission denied to access bucket: {bucket_name}")
        elif error_code == '404':
            print(f"⨯ Bucket not found: {bucket_name}")
        else:
            print(f"⨯ Error accessing bucket: {e}")
        return False
    except Exception as e:
        print(f"⨯ Unexpected error accessing bucket: {e}")
        return False

def check_object_exists(s3_client, bucket_name, key):
    """Check if an object exists in S3"""
    try:
        s3_client.head_object(Bucket=bucket_name, Key=key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        else:
            print(f"⨯ Error checking if object exists: {e}")
            return False

def migrate_images(delete_old_files=False):
    """Migrate blog images from static/ to images/ directory"""
    # Check S3 configuration
    if not check_s3_configuration():
        print("S3 configuration check failed. Please check your settings.")
        return False
        
    # Get all BlogImages records
    blog_images = BlogImages.objects.all()
    print(f"Found {len(blog_images)} BlogImages records to check")
    
    # Configure S3 client
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            endpoint_url=getattr(settings, 'AWS_S3_ENDPOINT_URL', None)
        )
    except Exception as e:
        print(f"⨯ Failed to create S3 client: {e}")
        return False
    
    # Get bucket name
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    
    # Verify S3 access
    if not verify_s3_access(s3, bucket_name):
        return False
        
    # Process each image
    migrated_count = 0
    error_count = 0
    skipped_count = 0
    already_correct_count = 0
    
    for i, img in enumerate(blog_images, 1):
        print(f"Processing image {i}/{len(blog_images)}...")
        
        if not img.image or not img.image.name:
            print(f"  Skipping empty image record")
            skipped_count += 1
            continue
            
        # Images already in the correct location
        if img.image.name.startswith('images/'):
            print(f"  ✓ Image already in correct location: {img.image.name}")
            already_correct_count += 1
            continue
            
        # Check if the image is in 'static/' directory
        if img.image.name.startswith('static/'):
            old_key = img.image.name
            new_key = 'images/' + old_key.replace('static/', '', 1)
            
            print(f"  Migrating: {old_key} -> {new_key}")
            
            # First check if the source object exists
            if not check_object_exists(s3, bucket_name, old_key):
                print(f"  ⨯ Source file does not exist in S3: {old_key}")
                error_count += 1
                continue
                
            # Check if the destination already exists
            if check_object_exists(s3, bucket_name, new_key):
                print(f"  ! Destination file already exists: {new_key}")
                # We can still update the database record
            
            try:
                # Copy object to new location in S3
                s3.copy_object(
                    CopySource={'Bucket': bucket_name, 'Key': old_key},
                    Bucket=bucket_name,
                    Key=new_key
                )
                
                # Update the database record
                img.image.name = new_key
                img.save()
                
                # Delete old object if requested
                if delete_old_files:
                    print(f"  Deleting old file: {old_key}")
                    s3.delete_object(Bucket=bucket_name, Key=old_key)
                
                migrated_count += 1
                print(f"  ✓ Successfully migrated {old_key} to {new_key}")
                
                # Small delay to avoid API rate limits
                time.sleep(0.2)
                
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code')
                print(f"  ⨯ S3 error ({error_code}) migrating {old_key}: {e}")
                error_count += 1
            except Exception as e:
                print(f"  ⨯ Error migrating {old_key}: {e}")
                error_count += 1
    
    # Print summary
    print("\nMigration Summary:")
    print(f"  Total records checked: {len(blog_images)}")
    print(f"  Already in correct location: {already_correct_count}")
    print(f"  Successfully migrated: {migrated_count}")
    print(f"  Skipped (empty records): {skipped_count}")
    print(f"  Errors encountered: {error_count}")
    
    if error_count > 0:
        print("\nWarning: Some errors occurred during migration.")
        print("You may need to manually fix these files.")
    
    return migrated_count > 0 or already_correct_count > 0

if __name__ == '__main__':
    # Check for command line arguments
    delete_old_files = False
    if len(sys.argv) > 1 and sys.argv[1] == '--delete-old-files':
        print("Will delete old files after migration.")
        delete_old_files = True
        
    success = migrate_images(delete_old_files)
    sys.exit(0 if success else 1)
