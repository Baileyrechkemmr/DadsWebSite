#!/usr/bin/env python3
import os
from django.conf import settings
from django.core.wsgi import get_wsgi_application

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'omimi.settings')
try:
    import django
    django.setup()
    
    print("Django settings loaded successfully!")
    print(f"USE_S3: {settings.USE_S3}")
    print(f"AWS_ACCESS_KEY_ID: {settings.AWS_ACCESS_KEY_ID[:10]}..." if settings.AWS_ACCESS_KEY_ID else "AWS_ACCESS_KEY_ID: Not set")
    print(f"AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}")
    print(f"DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")
    
    # Test S3 connection
    if settings.USE_S3:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
        
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            # Try to list objects in the bucket
            response = s3_client.list_objects_v2(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                MaxKeys=5
            )
            
            print("\n✅ S3 connection successful!")
            print(f"Found {response.get('KeyCount', 0)} objects in bucket")
            
            if 'Contents' in response:
                print("Sample files:")
                for obj in response['Contents'][:3]:
                    print(f"  - {obj['Key']}")
                    
        except NoCredentialsError:
            print("\n❌ AWS credentials not found or invalid")
        except ClientError as e:
            print(f"\n❌ S3 Error: {e}")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
    else:
        print("\n⚠️  S3 is disabled, using local storage")
        
except Exception as e:
    print(f"❌ Failed to setup Django: {e}")
