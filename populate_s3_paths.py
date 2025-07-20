#!/usr/bin/env python3
"""
Populate S3 Paths in Django Database

This script updates the Django SQLite database to point to static S3 paths
for various models that contain image fields. This allows the website to
know where to fetch files from S3 without having to upload files.

Usage:
    python3 populate_s3_paths.py [options]

Options:
    --skip-migrations     Skip running migrations (use if 'already exists' errors occur)
    --fresh-db            Delete existing database and create a new one
    --direct-mode         Bypass Django ORM entirely and directly populate paths
    --debug               Print detailed debug information
"""

import os
import sys
import argparse
import shutil
import sqlite3
import traceback
from datetime import datetime

# Parse arguments before Django setup to allow complete restart
parser = argparse.ArgumentParser(description='Populate S3 paths in Django database')
parser.add_argument('--skip-migrations', action='store_true', 
                  help='Skip running migrations (use if "already exists" errors occur)')
parser.add_argument('--fresh-db', action='store_true',
                  help='Delete existing database and create a new one')
parser.add_argument('--direct-mode', action='store_true',
                  help='Bypass Django ORM entirely and directly update SQLite')
parser.add_argument('--debug', action='store_true',
                  help='Print detailed debug information')
args = parser.parse_args()

# Handle the --fresh-db option before Django setup
if args.fresh_db:
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3')
    if os.path.exists(db_path):
        print(f"\n\033[33m⚠️ Deleting existing database: {db_path}\033[0m")
        try:
            os.remove(db_path)
            print("\033[32m✅ Database deleted successfully\033[0m")
        except Exception as e:
            print(f"\033[31m❌ Error deleting database: {str(e)}\033[0m")
            sys.exit(1)
    else:
        print(f"\033[33m⚠️ No existing database found at: {db_path}\033[0m")

# Direct mode doesn't need Django setup
if not args.direct_mode:
    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'omimi.settings')
        django.setup()
    except Exception as e:
        print(f"\033[31m❌ Error setting up Django: {str(e)}\033[0m")
        print("Try using --direct-mode to bypass Django setup")
        sys.exit(1)

# Default S3 bucket name (can be overridden by environment variable)
DEFAULT_BUCKET_NAME = 'ominisword-images'
BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', DEFAULT_BUCKET_NAME)

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

def debug_log(message):
    """Print debug message if debug mode is enabled"""
    if args.debug:
        print(f"\033[36m[DEBUG] {message}\033[0m")

def run_django_migrations():
    """Run Django migrations if needed"""
    if args.skip_migrations or args.direct_mode:
        print("\033[33m⚠️ Skipping migrations as requested\033[0m")
        return False
    
    print("\n\033[34m🔄 Checking and running migrations...\033[0m")
    try:
        from django.core.management import call_command
        call_command('migrate')
        print("\033[32m✅ Migrations applied successfully\033[0m")
        return True
    except Exception as e:
        print(f"\033[31m❌ Migration error: {str(e)}\033[0m")
        print("   Try running with --skip-migrations or --fresh-db option")
        print("   Or use --direct-mode to bypass Django ORM entirely")
        if args.debug:
            traceback.print_exc()
        return False

def get_s3_path(category, filename):
    """Generate S3 path for a file"""
    prefix = S3_PREFIXES.get(category, '')
    return f"{prefix}{filename}"

#-------------------------------------------
# Django ORM-based implementation
#-------------------------------------------

class DjangoPopulator:
    def __init__(self):
        from projects.models import Sword_img, Sword_sales, BlogImages, Blog
        self.Sword_img = Sword_img
        self.Sword_sales = Sword_sales
        self.BlogImages = BlogImages
        self.Blog = Blog
        self.stats = {'sword': 0, 'sales': 0, 'blog': 0}
        self.errors = []
    
    def populate_sword_images(self):
        """Update Sword_img model with S3 paths"""
        print(f"\n\033[34m🗡️ Updating Sword_img records...\033[0m")
        
        # Get all sword images
        sword_imgs = self.Sword_img.objects.all()
        
        if not sword_imgs.exists():
            # Create sample records if none exist
            print("   No Sword_img records found. Creating sample records...")
            for i, filename in enumerate(SAMPLE_FILES['sword'], 1):
                s3_path = get_s3_path('sword', filename)
                sword = self.Sword_img(item_number=i, description=f"Sample sword {i}")
                sword.image = s3_path
                sword.save()
                print(f"   \033[32m✅ Created sample Sword_img {i} with S3 path: {s3_path}\033[0m")
                self.stats['sword'] += 1
        else:
            # Update existing records
            for i, sword in enumerate(sword_imgs):
                try:
                    if i < len(SAMPLE_FILES['sword']):
                        filename = SAMPLE_FILES['sword'][i]
                    else:
                        filename = f"sword_{sword.item_number}.jpg"
                    
                    s3_path = get_s3_path('sword', filename)
                    sword.image = s3_path
                    sword.save()
                    print(f"   \033[32m✅ Updated Sword_img {sword.item_number} with S3 path: {s3_path}\033[0m")
                    self.stats['sword'] += 1
                except Exception as e:
                    error_msg = f"Error updating Sword_img {sword.item_number}: {str(e)}"
                    print(f"   \033[31m❌ {error_msg}\033[0m")
                    if args.debug:
                        traceback.print_exc()
                    self.errors.append(error_msg)
    
    def populate_sword_sales(self):
        """Update Sword_sales model with S3 paths"""
        print(f"\n\033[34m💰 Updating Sword_sales records...\033[0m")
        
        # Get all sword sales
        sword_sales = self.Sword_sales.objects.all()
        
        if not sword_sales.exists():
            # Create sample records if none exist
            print("   No Sword_sales records found. Creating sample records...")
            for i, filename in enumerate(SAMPLE_FILES['sales'], 1):
                s3_path = get_s3_path('sales', filename)
                sale = self.Sword_sales(
                    item_number=i,
                    description=f"Sample sword for sale {i}",
                    price=f"${i}00.00"
                )
                sale.image = s3_path
                sale.save()
                print(f"   \033[32m✅ Created sample Sword_sales {i} with S3 path: {s3_path}\033[0m")
                self.stats['sales'] += 1
        else:
            # Update existing records
            for i, sale in enumerate(sword_sales):
                try:
                    if i < len(SAMPLE_FILES['sales']):
                        filename = SAMPLE_FILES['sales'][i]
                    else:
                        filename = f"sale_item_{sale.item_number}.jpg"
                    
                    s3_path = get_s3_path('sales', filename)
                    sale.image = s3_path
                    sale.save()
                    print(f"   \033[32m✅ Updated Sword_sales {sale.item_number} with S3 path: {s3_path}\033[0m")
                    self.stats['sales'] += 1
                except Exception as e:
                    error_msg = f"Error updating Sword_sales {sale.item_number}: {str(e)}"
                    print(f"   \033[31m❌ {error_msg}\033[0m")
                    if args.debug:
                        traceback.print_exc()
                    self.errors.append(error_msg)
    
    def populate_blog_images(self):
        """Update BlogImages model with S3 paths"""
        print(f"\n\033[34m📝 Updating BlogImages records...\033[0m")
        
        # Get all blog images
        blog_images = self.BlogImages.objects.all()
        
        if not blog_images.exists():
            # Create sample records if none exist
            print("   No BlogImages records found. Creating sample records...")
            for i, filename in enumerate(SAMPLE_FILES['blog'], 1):
                s3_path = get_s3_path('blog', filename)
                blog_img = self.BlogImages()
                blog_img.image = s3_path
                blog_img.save()
                print(f"   \033[32m✅ Created sample BlogImages {i} with S3 path: {s3_path}\033[0m")
                self.stats['blog'] += 1
        else:
            # Update existing records
            for i, blog_img in enumerate(blog_images):
                try:
                    if i < len(SAMPLE_FILES['blog']):
                        filename = SAMPLE_FILES['blog'][i]
                    else:
                        filename = f"blog_image_{i+1}.jpg"
                    
                    s3_path = get_s3_path('blog', filename)
                    blog_img.image = s3_path
                    blog_img.save()
                    print(f"   \033[32m✅ Updated BlogImages {blog_img.id} with S3 path: {s3_path}\033[0m")
                    self.stats['blog'] += 1
                except Exception as e:
                    error_msg = f"Error updating BlogImages {blog_img.id}: {str(e)}"
                    print(f"   \033[31m❌ {error_msg}\033[0m")
                    if args.debug:
                        traceback.print_exc()
                    self.errors.append(error_msg)
    
    def associate_blog_images(self):
        """Associate BlogImages with Blog posts"""
        print(f"\n\033[34m🔄 Associating BlogImages with Blog posts...\033[0m")
        
        # Get all blog posts
        blogs = self.Blog.objects.all()
        blog_images = list(self.BlogImages.objects.all())
        
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
                
                print(f"   \033[32m✅ Associated {blog.images.count()} images with Blog {blog.id}\033[0m")
            except Exception as e:
                error_msg = f"Error associating images with Blog {blog.id}: {str(e)}"
                print(f"   \033[31m❌ {error_msg}\033[0m")
                if args.debug:
                    traceback.print_exc()
                self.errors.append(error_msg)
    
    def run(self):
        """Run the full population process"""
        print("=" * 70)
        print(f"\033[1;34m🚀 POPULATING S3 PATHS IN DJANGO DATABASE\033[0m")
        print("=" * 70)
        print(f"\033[34m📦 S3 Bucket: {BUCKET_NAME}\033[0m")
        print(f"\033[34m📂 Path Prefixes:\033[0m")
        for category, prefix in S3_PREFIXES.items():
            print(f"   \033[34m• {category}: {prefix}\033[0m")
        
        # Run all population methods
        self.populate_sword_images()
        self.populate_sword_sales()
        self.populate_blog_images()
        self.associate_blog_images()
        
        # Print summary
        print("\n" + "=" * 70)
        print("\033[1;34m📊 SUMMARY\033[0m")
        print(f"   \033[32m✅ Sword_img records updated: {self.stats['sword']}\033[0m")
        print(f"   \033[32m✅ Sword_sales records updated: {self.stats['sales']}\033[0m")
        print(f"   \033[32m✅ BlogImages records updated: {self.stats['blog']}\033[0m")
        
        if self.errors:
            print(f"   \033[33m⚠️ Errors encountered: {len(self.errors)}\033[0m")
            for error in self.errors[:5]:  # Show first 5 errors
                print(f"      \033[31m• {error}\033[0m")
            if len(self.errors) > 5:
                print(f"      ... and {len(self.errors) - 5} more errors")
        else:
            print("   \033[32m✨ No errors encountered\033[0m")
        
        print("=" * 70)
        print("\033[32m✅ Database population complete!\033[0m")
        print("\033[34m📝 Next steps:\033[0m")
        print("   1. Make sure your .env file has AWS credentials configured")
        print("   2. Make sure settings.py has S3 storage enabled")
        print("   3. Run the development server and check the website")
        print("   4. Verify images are loading from S3")

#-------------------------------------------
# Direct SQLite implementation (no Django ORM)
#-------------------------------------------

def direct_populate_database():
    """Directly populate the SQLite database without using Django ORM"""
    try:
        # Find the SQLite database file
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3')
        if not os.path.exists(db_path):
            print(f"\033[31m❌ Database not found: {db_path}\033[0m")
            print("   Please run Django migrations first or create the database")
            print("   Try: python3 manage.py migrate")
            return
        
        print("=" * 70)
        print(f"\033[1;34m🔧 DIRECT MODE: POPULATING S3 PATHS IN SQLITE DATABASE\033[0m")
        print("=" * 70)
        print(f"\033[34m📦 S3 Bucket: {BUCKET_NAME}\033[0m")
        print(f"\033[34m💾 Database: {db_path}\033[0m")
        
        # Create a backup of the database
        backup_path = f"{db_path}.backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        shutil.copy2(db_path, backup_path)
        print(f"\033[32m✅ Created database backup: {backup_path}\033[0m")
        
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the required tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {table[0] for table in cursor.fetchall()}
        debug_log(f"Found tables: {tables}")
        
        required_tables = [
            'projects_sword_img',
            'projects_sword_sales',
            'projects_blogimages',
            'projects_blog',
            'projects_blog_images'
        ]
        
        # Create tables if they don't exist
        if 'projects_sword_img' not in tables:
            print("\033[33m⚠️ Creating projects_sword_img table...\033[0m")
            cursor.execute("""
            CREATE TABLE "projects_sword_img" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "item_number" integer NOT NULL,
                "image" varchar(100) NULL,
                "description" text NOT NULL
            );
            """)
            conn.commit()
        
        if 'projects_sword_sales' not in tables:
            print("\033[33m⚠️ Creating projects_sword_sales table...\033[0m")
            cursor.execute("""
            CREATE TABLE "projects_sword_sales" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "item_number" integer NOT NULL,
                "image" varchar(100) NULL,
                "description" text NOT NULL,
                "price" varchar(50) NOT NULL
            );
            """)
            conn.commit()
            
        if 'projects_blogimages' not in tables:
            print("\033[33m⚠️ Creating projects_blogimages table...\033[0m")
            cursor.execute("""
            CREATE TABLE "projects_blogimages" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "image" varchar(100) NULL
            );
            """)
            conn.commit()
        
        # Populate Sword_img table
        print(f"\n\033[34m🗡️ Updating Sword_img records...\033[0m")
        cursor.execute("SELECT COUNT(*) FROM projects_sword_img;")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Create sample records
            print("   No Sword_img records found. Creating sample records...")
            for i, filename in enumerate(SAMPLE_FILES['sword'], 1):
                s3_path = get_s3_path('sword', filename)
                cursor.execute(
                    "INSERT INTO projects_sword_img (item_number, image, description) VALUES (?, ?, ?)",
                    (i, s3_path, f"Sample sword {i}")
                )
                print(f"   \033[32m✅ Created sample Sword_img {i} with S3 path: {s3_path}\033[0m")
            conn.commit()
        else:
            # Update existing records
            cursor.execute("SELECT id, item_number FROM projects_sword_img;")
            sword_items = cursor.fetchall()
            for i, (sword_id, item_number) in enumerate(sword_items):
                try:
                    if i < len(SAMPLE_FILES['sword']):
                        filename = SAMPLE_FILES['sword'][i]
                    else:
                        filename = f"sword_{item_number}.jpg"
                    
                    s3_path = get_s3_path('sword', filename)
                    cursor.execute(
                        "UPDATE projects_sword_img SET image=? WHERE id=?",
                        (s3_path, sword_id)
                    )
                    print(f"   \033[32m✅ Updated Sword_img {item_number} with S3 path: {s3_path}\033[0m")
                except Exception as e:
                    print(f"   \033[31m❌ Error updating Sword_img {item_number}: {str(e)}\033[0m")
                    if args.debug:
                        traceback.print_exc()
            conn.commit()
        
        # Populate Sword_sales table
        print(f"\n\033[34m💰 Updating Sword_sales records...\033[0m")
        cursor.execute("SELECT COUNT(*) FROM projects_sword_sales;")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Create sample records
            print("   No Sword_sales records found. Creating sample records...")
            for i, filename in enumerate(SAMPLE_FILES['sales'], 1):
                s3_path = get_s3_path('sales', filename)
                cursor.execute(
                    "INSERT INTO projects_sword_sales (item_number, image, description, price) VALUES (?, ?, ?, ?)",
                    (i, s3_path, f"Sample sword for sale {i}", f"${i}00.00")
                )
                print(f"   \033[32m✅ Created sample Sword_sales {i} with S3 path: {s3_path}\033[0m")
            conn.commit()
        else:
            # Update existing records
            cursor.execute("SELECT id, item_number FROM projects_sword_sales;")
            sale_items = cursor.fetchall()
            for i, (sale_id, item_number) in enumerate(sale_items):
                try:
                    if i < len(SAMPLE_FILES['sales']):
                        filename = SAMPLE_FILES['sales'][i]
                    else:
                        filename = f"sale_item_{item_number}.jpg"
                    
                    s3_path = get_s3_path('sales', filename)
                    cursor.execute(
                        "UPDATE projects_sword_sales SET image=? WHERE id=?",
                        (s3_path, sale_id)
                    )
                    print(f"   \033[32m✅ Updated Sword_sales {item_number} with S3 path: {s3_path}\033[0m")
                except Exception as e:
                    print(f"   \033[31m❌ Error updating Sword_sales {item_number}: {str(e)}\033[0m")
                    if args.debug:
                        traceback.print_exc()
            conn.commit()
        
        # Populate BlogImages table
        print(f"\n\033[34m📝 Updating BlogImages records...\033[0m")
        cursor.execute("SELECT COUNT(*) FROM projects_blogimages;")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Create sample records
            print("   No BlogImages records found. Creating sample records...")
            blog_image_ids = []
            for i, filename in enumerate(SAMPLE_FILES['blog'], 1):
                s3_path = get_s3_path('blog', filename)
                cursor.execute(
                    "INSERT INTO projects_blogimages (image) VALUES (?)",
                    (s3_path,)
                )
                blog_image_id = cursor.lastrowid
                blog_image_ids.append(blog_image_id)
                print(f"   \033[32m✅ Created sample BlogImages {blog_image_id} with S3 path: {s3_path}\033[0m")
            conn.commit()
            
            # Check if there are any blog posts to associate with images
            if 'projects_blog' in tables:
                cursor.execute("SELECT COUNT(*) FROM projects_blog;")
                blog_count = cursor.fetchone()[0]
                
                if blog_count > 0 and blog_image_ids and 'projects_blog_images' in tables:
                    print(f"\n\033[34m🔄 Associating BlogImages with Blog posts...\033[0m")
                    cursor.execute("SELECT id FROM projects_blog;")
                    blog_ids = [row[0] for row in cursor.fetchall()]
                    
                    # Clear existing associations
                    cursor.execute("DELETE FROM projects_blog_images;")
                    
                    # Create new associations
                    for i, blog_id in enumerate(blog_ids):
                        img_index = i % len(blog_image_ids)
                        cursor.execute(
                            "INSERT INTO projects_blog_images (blog_id, blogimages_id) VALUES (?, ?)",
                            (blog_id, blog_image_ids[img_index])
                        )
                        print(f"   \033[32m✅ Associated image {blog_image_ids[img_index]} with Blog {blog_id}\033[0m")
                        
                        # Add a second image sometimes
                        if i % 2 == 0 and len(blog_image_ids) > 1:
                            second_img_index = (i + 1) % len(blog_image_ids)
                            cursor.execute(
                                "INSERT INTO projects_blog_images (blog_id, blogimages_id) VALUES (?, ?)",
                                (blog_id, blog_image_ids[second_img_index])
                            )
                    conn.commit()
        else:
            # Update existing records
            cursor.execute("SELECT id FROM projects_blogimages;")
            blog_images = cursor.fetchall()
            for i, (blog_img_id,) in enumerate(blog_images):
                try:
                    if i < len(SAMPLE_FILES['blog']):
                        filename = SAMPLE_FILES['blog'][i]
                    else:
                        filename = f"blog_image_{i+1}.jpg"
                    
                    s3_path = get_s3_path('blog', filename)
                    cursor.execute(
                        "UPDATE projects_blogimages SET image=? WHERE id=?",
                        (s3_path, blog_img_id)
                    )
                    print(f"   \033[32m✅ Updated BlogImages {blog_img_id} with S3 path: {s3_path}\033[0m")
                except Exception as e:
                    print(f"   \033[31m❌ Error updating BlogImages {blog_img_id}: {str(e)}\033[0m")
                    if args.debug:
                        traceback.print_exc()
            conn.commit()
        
        # Print summary
        cursor.execute("SELECT COUNT(*) FROM projects_sword_img;")
        sword_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM projects_sword_sales;")
        sales_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM projects_blogimages;")
        blog_images_count = cursor.fetchone()[0]
        
        print("\n" + "=" * 70)
        print("\033[1;34m📊 SUMMARY\033[0m")
        print(f"   \033[32m✅ Sword_img records updated: {sword_count}\033[0m")
        print(f"   \033[32m✅ Sword_sales records updated: {sales_count}\033[0m")
        print(f"   \033[32m✅ BlogImages records updated: {blog_images_count}\033[0m")
        
        print("=" * 70)
        print("\033[32m✅ Database population complete!\033[0m")
        print("\033[34m📝 Next steps:\033[0m")
        print("   1. Make sure your .env file has AWS credentials configured")
        print("   2. Make sure settings.py has S3 storage enabled")
        print("   3. Run the development server and check the website")
        print("   4. Verify images are loading from S3")
        
        # Close connection
        conn.close()
        
    except Exception as e:
        print(f"\n\033[31m❌ Error in direct database population: {str(e)}\033[0m")
        if args.debug:
            traceback.print_exc()
        sys.exit(1)

#-------------------------------------------
# Main execution
#-------------------------------------------

if __name__ == "__main__":
    try:
        print("\033[1;32m=== Omimi Swords - S3 Paths Database Population Tool ===\033[0m")
        print(f"\033[34mRunning in {'debug mode' if args.debug else 'standard mode'}\033[0m")
        
        if args.direct_mode:
            # Use direct SQLite mode (no Django ORM)
            direct_populate_database()
        else:
            # Use Django ORM mode
            run_django_migrations()
            
            # Run the S3 path population
            try:
                populator = DjangoPopulator()
                populator.run()
            except Exception as e:
                print(f"\n\033[31m❌ Error in Django population: {str(e)}\033[0m")
                print("\033[33m⚠️ Trying direct mode might help if Django ORM is causing issues.\033[0m")
                print("   Run: python3 populate_s3_paths.py --direct-mode")
                if args.debug:
                    traceback.print_exc()
                sys.exit(1)
    except KeyboardInterrupt:
        print("\n\033[33m⚠️ Operation canceled by user\033[0m")
        sys.exit(0)
    except Exception as e:
        print(f"\n\033[31m❌ Unexpected error: {str(e)}\033[0m")
        if args.debug:
            traceback.print_exc()
        sys.exit(1)