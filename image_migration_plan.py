#!/usr/bin/env python3
"""
Image Migration Plan for Omimi Swords
Analyzes current images and plans S3 organization
"""

import os
import shutil
from pathlib import Path

class ImageMigrationPlan:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.migration_plan = {
            'static_ui': [],      # Website UI elements → static/
            'gallery_swords': [], # Sword images → gallery/swords/
            'gallery_sales': [],  # Sales images → gallery/sales/
            'blog_images': [],    # Blog content → blog/2024/12/
            'keep_local': [],     # System files to keep local
            'unknown': []         # Need manual categorization
        }
    
    def analyze_images(self):
        """Analyze all images and categorize them"""
        
        # Static UI Images (backgrounds, buttons, banners)
        ui_patterns = [
            'background', 'banner', 'button', 'logo', 'howard1', 
            'dadsBaner', 'profile_pic', 'about_button', 'blog.png',
            'classes', 'details_background'
        ]
        
        # Gallery Images (swords, weapons)
        gallery_patterns = [
            'sword', 'katana', 'blade', 'weapon', 'steel'
        ]
        
        # Blog Images (process photos, tutorials)
        blog_patterns = [
            '100_', 'PXL_', 'Graphic-Design', 'pexels', 'process'
        ]
        
        # System files to keep local
        system_patterns = [
            'ckeditor', 'admin', 'icons', 'hidpi'
        ]
        
        # Find all images
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'}
        
        for root, dirs, files in os.walk(self.base_dir):
            # Skip certain directories
            if any(skip in root for skip in ['.git', '__pycache__', 'node_modules']):
                continue
                
            for file in files:
                if Path(file).suffix.lower() in image_extensions:
                    full_path = Path(root) / file
                    relative_path = full_path.relative_to(self.base_dir)
                    file_lower = file.lower()
                    path_lower = str(relative_path).lower()
                    
                    # Categorize the image
                    if any(pattern in path_lower for pattern in system_patterns):
                        self.migration_plan['keep_local'].append({
                            'current_path': relative_path,
                            'reason': 'System/CKEditor file',
                            'size_kb': full_path.stat().st_size // 1024
                        })
                    elif any(pattern in file_lower for pattern in ui_patterns):
                        self.migration_plan['static_ui'].append({
                            'current_path': relative_path,
                            's3_path': f"static/ui/{file}",
                            'size_kb': full_path.stat().st_size // 1024
                        })
                    elif any(pattern in file_lower for pattern in gallery_patterns):
                        self.migration_plan['gallery_swords'].append({
                            'current_path': relative_path,
                            's3_path': f"gallery/swords/{file}",
                            'size_kb': full_path.stat().st_size // 1024
                        })
                    elif any(pattern in file_lower for pattern in blog_patterns) or 'blog' in path_lower:
                        self.migration_plan['blog_images'].append({
                            'current_path': relative_path,
                            's3_path': f"blog/2024/12/{file}",
                            'size_kb': full_path.stat().st_size // 1024
                        })
                    else:
                        self.migration_plan['unknown'].append({
                            'current_path': relative_path,
                            'suggested_category': self._suggest_category(file, str(relative_path)),
                            'size_kb': full_path.stat().st_size // 1024
                        })
    
    def _suggest_category(self, filename, path):
        """Suggest category for unknown images"""
        if 'media' in path and any(x in filename.lower() for x in ['100_', 'pxl_']):
            return 'blog_images'
        elif 'static' in path:
            return 'static_ui'
        elif any(x in filename.lower() for x in ['dog', 'animal', 'pet']):
            return 'blog_images'  # Assuming pet photos are for blog
        else:
            return 'gallery_swords'  # Default assumption
    
    def print_migration_plan(self):
        """Print detailed migration plan"""
        print("=" * 80)
        print("🗡️  OMIMI SWORDS - IMAGE MIGRATION PLAN")
        print("=" * 80)
        
        # Static UI Images
        if self.migration_plan['static_ui']:
            print(f"\n📱 STATIC UI IMAGES → S3: static/")
            print(f"   Will be used for: backgrounds, buttons, banners")
            total_size = sum(img['size_kb'] for img in self.migration_plan['static_ui'])
            print(f"   Total: {len(self.migration_plan['static_ui'])} files, {total_size:.1f} KB")
            for img in self.migration_plan['static_ui']:
                print(f"   ✓ {img['current_path']} → {img['s3_path']} ({img['size_kb']} KB)")
        
        # Gallery Images
        if self.migration_plan['gallery_swords']:
            print(f"\n🗡️  GALLERY IMAGES → S3: gallery/swords/")
            print(f"   Will be used for: sword showcase, portfolio")
            total_size = sum(img['size_kb'] for img in self.migration_plan['gallery_swords'])
            print(f"   Total: {len(self.migration_plan['gallery_swords'])} files, {total_size:.1f} KB")
            for img in self.migration_plan['gallery_swords']:
                print(f"   ✓ {img['current_path']} → {img['s3_path']} ({img['size_kb']} KB)")
        
        # Blog Images
        if self.migration_plan['blog_images']:
            print(f"\n📝 BLOG IMAGES → S3: blog/2024/12/")
            print(f"   Will be used for: blog posts, process photos")
            total_size = sum(img['size_kb'] for img in self.migration_plan['blog_images'])
            print(f"   Total: {len(self.migration_plan['blog_images'])} files, {total_size:.1f} KB")
            for img in self.migration_plan['blog_images']:
                print(f"   ✓ {img['current_path']} → {img['s3_path']} ({img['size_kb']} KB)")
        
        # Keep Local
        if self.migration_plan['keep_local']:
            print(f"\n💻 KEEP LOCAL (System Files)")
            print(f"   These stay in your Django static files")
            total_size = sum(img['size_kb'] for img in self.migration_plan['keep_local'])
            print(f"   Total: {len(self.migration_plan['keep_local'])} files, {total_size:.1f} KB")
            # Show just a few examples to avoid clutter
            for img in self.migration_plan['keep_local'][:5]:
                print(f"   ○ {img['current_path']} - {img['reason']}")
            if len(self.migration_plan['keep_local']) > 5:
                print(f"   ... and {len(self.migration_plan['keep_local']) - 5} more system files")
        
        # Unknown/Manual Review
        if self.migration_plan['unknown']:
            print(f"\n❓ NEEDS MANUAL REVIEW")
            print(f"   Please categorize these images:")
            for img in self.migration_plan['unknown']:
                print(f"   ? {img['current_path']} → Suggested: {img['suggested_category']}")
        
        # Summary
        total_to_s3 = (len(self.migration_plan['static_ui']) + 
                      len(self.migration_plan['gallery_swords']) + 
                      len(self.migration_plan['blog_images']))
        total_s3_size = (sum(img['size_kb'] for img in self.migration_plan['static_ui']) +
                        sum(img['size_kb'] for img in self.migration_plan['gallery_swords']) +
                        sum(img['size_kb'] for img in self.migration_plan['blog_images']))
        
        print(f"\n" + "=" * 80)
        print(f"📊 MIGRATION SUMMARY")
        print(f"   → S3: {total_to_s3} files ({total_s3_size/1024:.1f} MB)")
        print(f"   → Local: {len(self.migration_plan['keep_local'])} system files")
        print(f"   → Review: {len(self.migration_plan['unknown'])} files")
        print(f"   💰 Estimated S3 cost: ${(total_s3_size/1024/1024) * 0.023:.2f}/month")
        print("=" * 80)
    
    def generate_s3_upload_script(self):
        """Generate boto3 script for uploading to S3"""
        script = '''#!/usr/bin/env python3
"""
S3 Upload Script for Omimi Swords Images
Run this after AWS credentials are configured
"""

import boto3
import os
from pathlib import Path

# Configuration
BUCKET_NAME = 'omimi-media-bucket'
BASE_DIR = Path(__file__).parent

def upload_to_s3():
    s3 = boto3.client('s3')
    
    # Upload files
    uploads = [
'''
        
        # Add static UI files
        for img in self.migration_plan['static_ui']:
            script += f'        ("{img["current_path"]}", "{img["s3_path"]}"),\n'
        
        # Add gallery files
        for img in self.migration_plan['gallery_swords']:
            script += f'        ("{img["current_path"]}", "{img["s3_path"]}"),\n'
        
        # Add blog files
        for img in self.migration_plan['blog_images']:
            script += f'        ("{img["current_path"]}", "{img["s3_path"]}"),\n'
        
        script += '''    ]
    
    for local_path, s3_path in uploads:
        try:
            full_local_path = BASE_DIR / local_path
            if full_local_path.exists():
                print(f"Uploading {local_path} → s3://{BUCKET_NAME}/{s3_path}")
                s3.upload_file(
                    str(full_local_path), 
                    BUCKET_NAME, 
                    s3_path,
                    ExtraArgs={'ContentType': 'image/jpeg' if local_path.endswith(('.jpg', '.jpeg')) else 'image/png'}
                )
                print(f"✓ Success")
            else:
                print(f"✗ File not found: {local_path}")
        except Exception as e:
            print(f"✗ Error uploading {local_path}: {e}")

if __name__ == "__main__":
    print("🚀 Starting S3 upload...")
    upload_to_s3()
    print("✅ Upload complete!")
'''
        
        return script

if __name__ == "__main__":
    # Run the analysis
    planner = ImageMigrationPlan(".")
    planner.analyze_images()
    planner.print_migration_plan()
    
    # Save upload script
    upload_script = planner.generate_s3_upload_script()
    with open("s3_upload_script.py", "w") as f:
        f.write(upload_script)
    print(f"\n💾 S3 upload script saved as: s3_upload_script.py")
    print(f"   Run this after AWS credentials are configured!")