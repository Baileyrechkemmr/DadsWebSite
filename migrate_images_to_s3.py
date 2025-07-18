#!/usr/bin/env python3
"""
Migrate Omimi Swords Images to S3
Uploads local images to S3 with proper organization
"""

import boto3
import os
from pathlib import Path
from botocore.exceptions import ClientError
import mimetypes

class S3ImageMigrator:
    def __init__(self):
        # AWS Configuration from environment
        self.bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME', 'ominisword-images')
        self.aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.region = os.environ.get('AWS_S3_REGION', 'us-east-1')
        
        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.region
        )
        
    def test_s3_connection(self):
        """Test S3 connection and list current bucket contents"""
        try:
            print(f"🔍 Checking S3 bucket: {self.bucket_name}")
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            
            if 'Contents' in response:
                print(f"📁 Current files in bucket ({len(response['Contents'])} items):")
                for obj in response['Contents'][:10]:  # Show first 10
                    size_kb = obj['Size'] / 1024
                    print(f"   • {obj['Key']} ({size_kb:.1f} KB)")
                if len(response['Contents']) > 10:
                    print(f"   ... and {len(response['Contents']) - 10} more files")
            else:
                print("📁 Bucket is empty - ready for migration!")
            
            return True
        except ClientError as e:
            print(f"❌ S3 connection failed: {e}")
            return False
    
    def get_content_type(self, file_path):
        """Get MIME type for file"""
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            return mime_type
        # Default based on extension
        ext = Path(file_path).suffix.lower()
        if ext in ['.jpg', '.jpeg']:
            return 'image/jpeg'
        elif ext == '.png':
            return 'image/png'
        elif ext == '.webp':
            return 'image/webp'
        elif ext == '.gif':
            return 'image/gif'
        else:
            return 'binary/octet-stream'
    
    def upload_file(self, local_path, s3_path):
        """Upload a single file to S3"""
        try:
            local_file = Path(local_path)
            if not local_file.exists():
                print(f"❌ File not found: {local_path}")
                return False
            
            content_type = self.get_content_type(str(local_file))
            size_kb = local_file.stat().st_size / 1024
            
            print(f"📤 Uploading {local_path} → s3://{self.bucket_name}/{s3_path} ({size_kb:.1f} KB)")
            
            self.s3_client.upload_file(
                str(local_file),
                self.bucket_name,
                s3_path,
                ExtraArgs={
                    'ContentType': content_type
                    # Removed ACL since bucket doesn't allow ACLs
                }
            )
            
            # Verify upload
            s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_path}"
            print(f"✅ Success! URL: {s3_url}")
            return True
            
        except ClientError as e:
            print(f"❌ Upload failed for {local_path}: {e}")
            return False
    
    def migrate_all_images(self):
        """Migrate all categorized images to S3"""
        
        # Define migration mappings
        migrations = {
            # Static UI Images
            'static_ui': [
                ('projects/static/dadsBanerOne.jpeg', 'static/ui/dadsBanerOne.jpeg'),
                ('projects/static/howard1.jpeg', 'static/ui/howard1.jpeg'),
                ('projects/static/classes_image_1.png', 'static/ui/classes_image_1.png'),
                ('projects/static/classesContentPage.png', 'static/ui/classesContentPage.png'),
                ('projects/static/blog.png', 'static/ui/blog.png'),
                ('projects/static/about_button.png', 'static/ui/about_button.png'),
                ('projects/static/profile_pic_1.png', 'static/ui/profile_pic_1.png'),
                ('projects/static/details_background.png', 'static/ui/details_background.png'),
                # Also check static/ directory
                ('static/dadsBanerOne.jpeg', 'static/ui/dadsBanerOne.jpeg'),
                ('static/howard1.jpeg', 'static/ui/howard1.jpeg'),
                ('static/classes_image_1.png', 'static/ui/classes_image_1.png'),
                ('static/classesContentPage.png', 'static/ui/classesContentPage.png'),
                ('static/blog.png', 'static/ui/blog.png'),
                ('static/about_button.png', 'static/ui/about_button.png'),
                ('static/profile_pic_1.png', 'static/ui/profile_pic_1.png'),
                ('static/details_background.png', 'static/ui/details_background.png'),
            ],
            
            # Gallery Images (Swords)
            'gallery': [
                ('images/sword_one.webp', 'gallery/swords/sword_one.webp'),
                ('images/14.jpg', 'gallery/swords/14.jpg'),
                ('images/cef.jpg', 'gallery/swords/cef.jpg'),
            ],
            
            # Blog Images
            'blog': [
                ('media/blog_images/100_3589.png', 'blog/2024/12/100_3589.png'),
                ('media/blog_images/100_4278.png', 'blog/2024/12/100_4278.png'),
                ('media/blog_images/100_4285.png', 'blog/2024/12/100_4285.png'),
                ('media/blog_images/100_4286.png', 'blog/2024/12/100_4286.png'),
                ('media/blog_images/100_4303.png', 'blog/2024/12/100_4303.png'),
                ('media/blog_images/100_4308.png', 'blog/2024/12/100_4308.png'),
                ('images/PXL_20230207_214659597_1.jpg', 'blog/2024/12/PXL_20230207_214659597_1.jpg'),
                ('images/Graphic-Design-Course-in-Bangalore.jpg', 'blog/2024/12/Graphic-Design-Course-in-Bangalore.jpg'),
                ('images/pexels-pixabay-45201_1.jpg', 'blog/2024/12/pexels-pixabay-45201_1.jpg'),
                # Additional blog candidates
                ('images/100_3589.png', 'blog/2024/12/100_3589_alt.png'),
                ('images/100_4282.png', 'blog/2024/12/100_4282.png'),
                ('images/100_4283.png', 'blog/2024/12/100_4283.png'),
                ('images/100_4286.png', 'blog/2024/12/100_4286_alt.png'),
            ],
            
            # Unknown/Personal Images (categorizing as blog for now)
            'personal': [
                ('images/aang.jpg', 'blog/2024/12/personal/aang.jpg'),
                ('images/cowhead.jpg', 'blog/2024/12/personal/cowhead.jpg'),
                ('images/dog_outline.jpg', 'blog/2024/12/personal/dog_outline.jpg'),
                ('images/momo.jpg', 'blog/2024/12/personal/momo.jpg'),
                ('images/mydog.jpg', 'blog/2024/12/personal/mydog.jpg'),
                ('images/Snapchat-1456340180.jpg', 'blog/2024/12/personal/Snapchat-1456340180.jpg'),
                ('images/zQvr9qX_-_Imgur.jpg', 'blog/2024/12/personal/zQvr9qX_-_Imgur.jpg'),
            ]
        }
        
        total_success = 0
        total_attempts = 0
        
        for category, file_list in migrations.items():
            print(f"\n🗂️  MIGRATING {category.upper()} IMAGES")
            print("=" * 50)
            
            for local_path, s3_path in file_list:
                total_attempts += 1
                if self.upload_file(local_path, s3_path):
                    total_success += 1
                print()  # Add spacing
        
        # Summary
        print("=" * 80)
        print(f"📊 MIGRATION SUMMARY")
        print(f"✅ Successfully uploaded: {total_success}/{total_attempts} files")
        print(f"🌐 S3 Bucket: https://{self.bucket_name}.s3.{self.region}.amazonaws.com/")
        print("=" * 80)
        
        return total_success, total_attempts

def main():
    print("🗡️  OMIMI SWORDS - S3 IMAGE MIGRATION")
    print("=" * 80)
    
    # Environment variables should already be available
    # Check if credentials are set
    if not os.environ.get('AWS_ACCESS_KEY_ID'):
        print("❌ AWS_ACCESS_KEY_ID not found in environment")
        print("💡 Make sure to run: export AWS_ACCESS_KEY_ID=your_key")
        return
    
    migrator = S3ImageMigrator()
    
    # Test connection first
    if not migrator.test_s3_connection():
        print("❌ Cannot connect to S3. Please check your credentials.")
        return
    
    print("\n🚀 Starting image migration...")
    success_count, total_count = migrator.migrate_all_images()
    
    if success_count == total_count:
        print("\n🎉 All images migrated successfully!")
        print("Next steps:")
        print("1. Update Django models to use ImageField")
        print("2. Configure Django settings for S3")
        print("3. Update templates to use S3 URLs")
        print("4. Clean up local image files")
    else:
        print(f"\n⚠️  Migration completed with some issues ({success_count}/{total_count})")
        print("Review the output above for failed uploads.")

if __name__ == "__main__":
    main()