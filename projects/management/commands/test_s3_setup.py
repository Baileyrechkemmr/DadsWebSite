"""
Django management command to test S3 static and media file configuration.
This helps verify that S3 is properly configured for admin page assets.

Usage:
    python manage.py test_s3_setup
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.files.storage import get_storage_class
import boto3
from botocore.exceptions import ClientError
import os


class Command(BaseCommand):
    help = 'Test S3 configuration for static and media files'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔍 Testing S3 Configuration...\n')
        )
        
        # Test 1: Check environment variables
        self.test_env_vars()
        
        # Test 2: Check S3 connection
        self.test_s3_connection()
        
        # Test 3: Check storage backends
        self.test_storage_backends()
        
        # Test 4: Check critical admin files
        self.test_admin_files()
        
        self.stdout.write(
            self.style.SUCCESS('\n✅ S3 Configuration Test Complete!')
        )

    def test_env_vars(self):
        self.stdout.write('📋 Checking Environment Variables...')
        
        required_vars = [
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY', 
            'AWS_STORAGE_BUCKET_NAME'
        ]
        
        missing_vars = []
        for var in required_vars:
            value = getattr(settings, var, None)
            if value:
                self.stdout.write(f'  ✅ {var}: {"*" * 10}')
            else:
                missing_vars.append(var)
                self.stdout.write(self.style.ERROR(f'  ❌ {var}: Not set'))
        
        if missing_vars:
            self.stdout.write(
                self.style.ERROR(f'Missing required variables: {", ".join(missing_vars)}')
            )
            return False
        return True

    def test_s3_connection(self):
        self.stdout.write('\n🔌 Testing S3 Connection...')
        
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            # Test bucket access
            response = s3_client.head_bucket(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
            self.stdout.write(f'  ✅ Connected to bucket: {settings.AWS_STORAGE_BUCKET_NAME}')
            
            # List some objects to verify permissions
            objects = s3_client.list_objects_v2(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Prefix='static/',
                MaxKeys=5
            )
            
            if 'Contents' in objects:
                self.stdout.write(f'  ✅ Found {len(objects["Contents"])} static files in S3')
                for obj in objects['Contents'][:3]:
                    self.stdout.write(f'    📁 {obj["Key"]}')
            else:
                self.stdout.write('  ⚠️  No static files found in S3 (may need collectstatic)')
                
        except ClientError as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ S3 Connection Failed: {e}')
            )
            return False
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Unexpected error: {e}')
            )
            return False
        
        return True

    def test_storage_backends(self):
        self.stdout.write('\n📦 Testing Storage Backends...')
        
        try:
            # Test static storage
            static_storage = get_storage_class(settings.STATICFILES_STORAGE)()
            self.stdout.write(f'  ✅ Static Storage: {static_storage.__class__.__name__}')
            self.stdout.write(f'     Location: {getattr(static_storage, "location", "N/A")}')
            
            # Test media storage  
            if hasattr(settings, 'DEFAULT_FILE_STORAGE'):
                media_storage = get_storage_class(settings.DEFAULT_FILE_STORAGE)()
                self.stdout.write(f'  ✅ Media Storage: {media_storage.__class__.__name__}')
                self.stdout.write(f'     Location: {getattr(media_storage, "location", "N/A")}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Storage Backend Error: {e}')
            )

    def test_admin_files(self):
        self.stdout.write('\n🎨 Testing Critical Admin Files...')
        
        critical_files = [
            'admin/css/base.css',
            'admin/css/forms.css', 
            'admin/js/core.js',
            'admin/img/icon-addlink.svg'
        ]
        
        for file_path in critical_files:
            try:
                found_file = finders.find(file_path)
                if found_file:
                    self.stdout.write(f'  ✅ Found: {file_path}')
                else:
                    self.stdout.write(f'  ❌ Missing: {file_path}')
            except Exception as e:
                self.stdout.write(f'  ⚠️  Error finding {file_path}: {e}')

        # Test actual URLs
        self.stdout.write('\n🌐 Testing Static URLs...')
        from django.contrib.staticfiles.storage import staticfiles_storage
        
        base_css_url = staticfiles_storage.url('admin/css/base.css')
        self.stdout.write(f'  📍 Admin CSS URL: {base_css_url}')
        
        # Check if it's S3
        if 's3.amazonaws.com' in base_css_url or settings.AWS_STORAGE_BUCKET_NAME in base_css_url:
            self.stdout.write('  ✅ Using S3 for static files')
        else:
            self.stdout.write('  ⚠️  Not using S3 for static files')