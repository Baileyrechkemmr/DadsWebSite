#!/usr/bin/env python3
"""
Test S3 integration with Django settings
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'omimi.settings')
django.setup()

from django.conf import settings
from django.core.files.storage import default_storage

def test_s3_integration():
    print("🧪 Testing Django S3 Integration")
    print("=" * 50)
    
    # Test 1: Check Django settings
    print("📋 Django Settings:")
    print(f"   AWS_STORAGE_BUCKET_NAME: {getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'Not set')}")
    print(f"   MEDIA_URL: {getattr(settings, 'MEDIA_URL', 'Not set')}")
    print(f"   DEFAULT_FILE_STORAGE: {getattr(settings, 'DEFAULT_FILE_STORAGE', 'Not set')}")
    
    # Test 2: Test storage backend
    print(f"\n🔧 Storage Backend:")
    print(f"   Type: {type(default_storage)}")
    print(f"   Bucket: {getattr(default_storage, 'bucket_name', 'Not available')}")
    
    # Test 3: Check if we can list some files
    print(f"\n📁 Testing file listing:")
    try:
        # List first few files
        files = list(default_storage.listdir('')[1])[:5]  # Get files from root
        print(f"   ✅ Can access S3! Found {len(files)} files in root:")
        for file in files:
            print(f"      • {file}")
    except Exception as e:
        print(f"   ❌ Error listing files: {e}")
    
    # Test 4: Test specific image URLs
    print(f"\n🖼️  Testing Image URLs:")
    test_images = [
        'images/sword_one.webp',
        'static/blog.png', 
        'images/100_3589.png'
    ]
    
    for image_path in test_images:
        try:
            url = default_storage.url(image_path)
            print(f"   ✅ {image_path} → {url}")
        except Exception as e:
            print(f"   ❌ {image_path} → Error: {e}")
    
    # Test 5: Current vs Expected URLs
    print(f"\n🔗 URL Comparison:")
    expected_base = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/"
    actual_base = settings.MEDIA_URL
    
    print(f"   Expected: {expected_base}")
    print(f"   Actual:   {actual_base}")
    print(f"   Match: {'✅' if expected_base == actual_base else '❌'}")
    
    print("\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("   1. If URLs work ✅ → Update models to use ImageField")
    print("   2. If URLs fail ❌ → Fix settings configuration")
    
if __name__ == "__main__":
    test_s3_integration()