#!/usr/bin/env python3
"""
Populate S3 Paths in Django Database

This script updates the Django SQLite database to point to static S3 paths
for various models that contain image fields. This allows the website to
know where to fetch files from S3 without having to upload files.

Usage:
    python populate_s3_paths.py
"""

import os
import sys
import django
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'omimi.settings')
django.setup()

# Import models after Django setup
from projects.models import Sword_img, Sword_sales, BlogImages, Blog
from django.db.models.fields.files import FieldFile
from django.core.files.base import ContentFile

# Default S3 bucket name (can be overridden by environment variable)
DEFAULT_BUCKET_NAME = 'ominisword-images'

# S3 path mapping for different model types
S3_PREFIXES = {
    'sword': 'gallery/swords/',
    'sales': 'gallery/sales/',
    'blog': 'blog/2024/12/',
    'ui': 'static/ui/'
}

# Sample file names for each category (used if no files are found)
SAMPLE_FILES = {
    'sword': ['sword_one.webp', '14.jpg', 'cef.jpg'],
    'sales': ['sale_item_1.jpg', 'sale_item_2.jpg', 'sale_item_3.jpg'],
    'blog': ['blog_image_1.jpg', '100_3589.png', '100_4278.png'],
    'ui': ['blog.png', 'dadsBanerOne.jpeg', 'howard1.jpeg']
}

class S3PathPopulator:
    def __init__(self):
        self.bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME', DEFAULT_BUCKET_NAME)
        self.stats = {'sword': 0, 'sales': 0, 'blog': 0}
        self.errors = []
    
    def _get_s3_path(self, category, filename):
        """Generate S3 path for a file"""
        prefix = S3_PREFIXES.get(category, '')
        return f"{prefix}{filename}"
    
    def populate_sword_images(self):
        """Update Sword_img model with S3 paths"""
        print(f"\n🗡️  Updating Sword_img records...")
        
        # Get all sword images
        sword_imgs = Sword_img.objects.all()
        
        if not sword_imgs.exists():
            # Create sample records if none exist
            print("   No Sword_img records found. Creating sample records...")
            for i, filename in enumerate(SAMPLE_FILES['sword'], 1):
                s3_path = self._get_s3_path('sword', filename)
                sword = Sword_img(item_number=i, description=f"Sample sword {i}")
                sword.image = s3_path
                sword.save()
                print(f"   ✅ Created sample Sword_img {i} with S3 path: {s3_path}")
                self.stats['sword'] += 1
        else:
            # Update existing records
            for i, sword in enumerate(sword_imgs):
                try:
                    if i < len(SAMPLE_FILES['sword']):
                        filename = SAMPLE_FILES['sword'][i]
                    else:
                        filename = f"sword_{sword.item_number}.jpg"
                    
                    s3_path = self._get_s3_path('sword', filename)
                    sword.image = s3_path
                    sword.save()
                    print(f"   ✅ Updated Sword_img {sword.item_number} with S3 path: {s3_path}")
                    self.stats['sword'] += 1
                except Exception as e:
                    error_msg = f"Error updating Sword_img {sword.item_number}: {str(e)}"
                    print(f"   ❌ {error_msg}")
                    self.errors.append(error_msg)
    
    def populate_sword_sales(self):
        """Update Sword_sales model with S3 paths"""
        print(f"\n💰 Updating Sword_sales records...")
        
        # Get all sword sales
        sword_sales = Sword_sales.objects.all()
        
        if not sword_sales.exists():
            # Create sample records if none exist
            print("   No Sword_sales records found. Creating sample records...")
            for i, filename in enumerate(SAMPLE_FILES['sales'], 1):
                s3_path = self._get_s3_path('sales', filename)
                sale = Sword_sales(
                    item_number=i,
                    description=f"Sample sword for sale {i}",
                    price=f"${i}00.00"
                )
                sale.image = s3_path
                sale.save()
                print(f"   ✅ Created sample Sword_sales {i} with S3 path: {s3_path}")
                self.stats['sales'] += 1
        else:
            # Update existing records
            for i, sale in enumerate(sword_sales):
                try:
                    if i < len(SAMPLE_FILES['sales']):
                        filename = SAMPLE_FILES['sales'][i]
                    else:
                        filename = f"sale_item_{sale.item_number}.jpg"
                    
                    s3_path = self._get_s3_path('sales', filename)
                    sale.image = s3_path
                    sale.save()
                    print(f"   ✅ Updated Sword_sales {sale.item_number} with S3 path: {s3_path}")
                    self.stats['sales'] += 1
                except Exception as e:
                    error_msg = f"Error updating Sword_sales {sale.item_number}: {str(e)}"
                    print(f"   ❌ {error_msg}")
                    self.errors.append(error_msg)
    
    def populate_blog_images(self):
        """Update BlogImages model with S3 paths"""
        print(f"\n📝 Updating BlogImages records...")
        
        # Get all blog images
        blog_images = BlogImages.objects.all()
        
        if not blog_images.exists():
            # Create sample records if none exist
            print("   No BlogImages records found. Creating sample records...")
            for i, filename in enumerate(SAMPLE_FILES['blog'], 1):
                s3_path = self._get_s3_path('blog', filename)
                blog_img = BlogImages()
                blog_img.image = s3_path
                blog_img.save()
                print(f"   ✅ Created sample BlogImages {i} with S3 path: {s3_path}")
                self.stats['blog'] += 1
        else:
            # Update existing records
            for i, blog_img in enumerate(blog_images):
                try:
                    if i < len(SAMPLE_FILES['blog']):
                        filename = SAMPLE_FILES['blog'][i]
                    else:
                        filename = f"blog_image_{i+1}.jpg"
                    
                    s3_path = self._get_s3_path('blog', filename)
                    blog_img.image = s3_path
                    blog_img.save()
                    print(f"   ✅ Updated BlogImages {blog_img.id} with S3 path: {s3_path}")
                    self.stats['blog'] += 1
                except Exception as e:
                    error_msg = f"Error updating BlogImages {blog_img.id}: {str(e)}"
                    print(f"   ❌ {error_msg}")
                    self.errors.append(error_msg)
    
    def associate_blog_images(self):
        """Associate BlogImages with Blog posts"""
        print(f"\n🔄 Associating BlogImages with Blog posts...")
        
        # Get all blog posts
        blogs = Blog.objects.all()
        blog_images = list(BlogImages.objects.all())
        
        if not blogs.exists():
            print("   No Blog records found. Skipping association.")
            return
        
        if not blog_images:
            print("   No BlogImages records found. Skipping association.")
            return
        
        # Associate images with blog posts
        for i, blog in enumerate(blogs):
            try:
                # Assign 1-2 images to each blog post in round-robin fashion
                blog.images.clear()
                
                # Add first image
                img_index = i % len(blog_images)
                blog.images.add(blog_images[img_index])
                
                # Possibly add a second image
                if i % 2 == 0 and len(blog_images) > 1:
                    second_img_index = (i + 1) % len(blog_images)
                    blog.images.add(blog_images[second_img_index])
                
                print(f"   ✅ Associated {blog.images.count()} images with Blog {blog.id}")
            except Exception as e:
                error_msg = f"Error associating images with Blog {blog.id}: {str(e)}"
                print(f"   ❌ {error_msg}")
                self.errors.append(error_msg)
    
    def run(self):
        """Run the full population process"""
        print("=" * 70)
        print(f"🚀 POPULATING S3 PATHS IN DJANGO DATABASE")
        print("=" * 70)
        print(f"📦 S3 Bucket: {self.bucket_name}")
        print(f"🗂️  Path Prefixes:")
        for category, prefix in S3_PREFIXES.items():
            print(f"   • {category}: {prefix}")
        
        # Run all population methods
        self.populate_sword_images()
        self.populate_sword_sales()
        self.populate_blog_images()
        self.associate_blog_images()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 SUMMARY")
        print(f"   ✅ Sword_img records updated: {self.stats['sword']}")
        print(f"   ✅ Sword_sales records updated: {self.stats['sales']}")
        print(f"   ✅ BlogImages records updated: {self.stats['blog']}")
        
        if self.errors:
            print(f"   ⚠️ Errors encountered: {len(self.errors)}")
            for error in self.errors[:5]:  # Show first 5 errors
                print(f"      • {error}")
            if len(self.errors) > 5:
                print(f"      ... and {len(self.errors) - 5} more errors")
        else:
            print("   ✨ No errors encountered")
        
        print("=" * 70)
        print("✅ Database population complete!")
        print("📝 Next steps:")
        print("   1. Make sure your .env file has AWS credentials configured")
        print("   2. Make sure settings.py has S3 storage enabled")
        print("   3. Run the development server and check the website")
        print("   4. Verify images are loading from S3")

if __name__ == "__main__":
    try:
        populator = S3PathPopulator()
        populator.run()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)