#!/usr/bin/env python3
"""
Explore what's currently in the S3 bucket
"""

import boto3
import os
from collections import defaultdict

def explore_s3_bucket():
    # AWS Configuration
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME', 'ominisword-images')
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    region = os.environ.get('AWS_S3_REGION', 'us-east-1')
    
    # Initialize S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=region
    )
    
    print("🗡️  OMIMI SWORDS - S3 BUCKET EXPLORER")
    print("=" * 80)
    print(f"📁 Bucket: {bucket_name}")
    print(f"🌐 Region: {region}")
    
    try:
        # List all objects
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' not in response:
            print("📁 Bucket is empty")
            return
        
        objects = response['Contents']
        print(f"📊 Total files: {len(objects)}")
        
        # Organize by folder/prefix
        folders = defaultdict(list)
        total_size = 0
        
        for obj in objects:
            key = obj['Key']
            size = obj['Size']
            total_size += size
            
            # Get folder/prefix
            if '/' in key:
                folder = key.split('/')[0]
            else:
                folder = 'root'
            
            folders[folder].append({
                'key': key,
                'size': size,
                'size_kb': size / 1024,
                'modified': obj['LastModified']
            })
        
        print(f"💾 Total size: {total_size / (1024*1024):.1f} MB")
        print()
        
        # Show folder breakdown
        print("📂 FOLDER STRUCTURE:")
        print("-" * 60)
        
        for folder, files in sorted(folders.items()):
            folder_size = sum(f['size'] for f in files)
            print(f"📁 {folder}/ ({len(files)} files, {folder_size/(1024*1024):.1f} MB)")
            
            # Show sample files from each folder
            sample_files = sorted(files, key=lambda x: x['size'], reverse=True)[:5]
            for file in sample_files:
                print(f"   • {file['key']} ({file['size_kb']:.1f} KB)")
            
            if len(files) > 5:
                print(f"   ... and {len(files) - 5} more files")
            print()
        
        # Look for specific patterns
        print("🔍 IMAGE ANALYSIS:")
        print("-" * 60)
        
        # Count by extension
        extensions = defaultdict(int)
        sword_images = []
        blog_images = []
        ui_images = []
        
        for obj in objects:
            key = obj['Key'].lower()
            
            # Get extension
            if '.' in key:
                ext = key.split('.')[-1]
                extensions[ext] += 1
            
            # Categorize
            if any(word in key for word in ['sword', 'katana', 'blade', 'weapon']):
                sword_images.append(obj['Key'])
            elif any(word in key for word in ['100_', 'pxl_', 'blog', 'process']):
                blog_images.append(obj['Key'])
            elif any(word in key for word in ['banner', 'button', 'background', 'howard', 'profile']):
                ui_images.append(obj['Key'])
        
        print("📈 File Types:")
        for ext, count in sorted(extensions.items()):
            print(f"   • .{ext}: {count} files")
        
        print(f"\n🗡️  Potential Sword Images: {len(sword_images)}")
        for img in sword_images[:10]:
            print(f"   • {img}")
        if len(sword_images) > 10:
            print(f"   ... and {len(sword_images) - 10} more")
        
        print(f"\n📝 Potential Blog Images: {len(blog_images)}")
        for img in blog_images[:10]:
            print(f"   • {img}")
        if len(blog_images) > 10:
            print(f"   ... and {len(blog_images) - 10} more")
        
        print(f"\n📱 Potential UI Images: {len(ui_images)}")
        for img in ui_images[:10]:
            print(f"   • {img}")
        if len(ui_images) > 10:
            print(f"   ... and {len(ui_images) - 10} more")
        
        # Generate sample URLs
        print(f"\n🌐 SAMPLE S3 URLS:")
        print("-" * 60)
        sample_keys = [obj['Key'] for obj in objects[:3]]
        for key in sample_keys:
            url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{key}"
            print(f"• {url}")
        
        print("\n" + "=" * 80)
        print("✅ S3 bucket exploration complete!")
        print("💡 Your images are already in S3 - now we need to configure Django to use them properly.")
        
    except Exception as e:
        print(f"❌ Error exploring bucket: {e}")

if __name__ == "__main__":
    explore_s3_bucket()