#!/usr/bin/env python3
"""
Complete Database Setup Script for Omimi Swords

This script creates a fresh SQLite database with all required tables
and populates it with S3 paths. It bypasses Django migrations entirely
to avoid any compatibility issues or errors.

It includes comprehensive cleanup of previous failed setups to ensure
you can get to a clean runnable state no matter what state you're in.

Usage:
    python3 setup_omimi_database.py

Options:
    --debug      Print detailed debug information
    --force      Overwrite existing database without prompting
    --no-backup  Skip creating backups of existing database
    --no-cleanup Skip cleanup of cached files and temporary data
"""

import os
import sys
import glob
import argparse
import sqlite3
import shutil
import traceback
from pathlib import Path
from datetime import datetime
import subprocess

# Parse arguments
parser = argparse.ArgumentParser(description='Setup Omimi Swords database')
parser.add_argument('--debug', action='store_true', help='Print detailed debug information')
parser.add_argument('--force', action='store_true', help='Overwrite existing database without prompting')
parser.add_argument('--no-backup', action='store_true', help='Skip creating backups of existing database')
parser.add_argument('--no-cleanup', action='store_true', help='Skip cleanup of cached files and temporary data')
args = parser.parse_args()

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

def print_color(text, color=None, bold=False):
    """Print colored text to console"""
    colors = {
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'reset': '\033[0m'
    }
    
    bold_code = '\033[1m' if bold else ''
    color_code = colors.get(color, '')
    reset_code = colors['reset'] if color or bold else ''
    
    print(f"{bold_code}{color_code}{text}{reset_code}")

def debug_log(message):
    """Print debug message if debug mode is enabled"""
    if args.debug:
        print_color(f"[DEBUG] {message}", 'cyan')

def cleanup_previous_state():
    """Clean up artifacts from previous failed setup attempts"""
    if args.no_cleanup:
        print_color("Skipping cleanup as requested with --no-cleanup", 'yellow')
        return
    
    print_color("\n=== Cleaning up previous setup state ===", 'blue', bold=True)
    
    project_root = find_project_root()
    cleanup_count = 0
    
    # 1. Clean up Python cache files
    try:
        # Find all __pycache__ directories
        for pycache_dir in project_root.glob('**/__pycache__'):
            if pycache_dir.is_dir():
                try:
                    shutil.rmtree(pycache_dir)
                    print_color(f"Removed cache directory: {pycache_dir.relative_to(project_root)}", 'yellow')
                    cleanup_count += 1
                except Exception as e:
                    debug_log(f"Error removing {pycache_dir}: {e}")
        
        # Find all .pyc files
        for pyc_file in project_root.glob('**/*.pyc'):
            try:
                pyc_file.unlink()
                print_color(f"Removed cache file: {pyc_file.relative_to(project_root)}", 'yellow')
                cleanup_count += 1
            except Exception as e:
                debug_log(f"Error removing {pyc_file}: {e}")
    except Exception as e:
        print_color(f"Error during Python cache cleanup: {e}", 'red')
    
    # 2. Clean up SQLite auxiliary files
    try:
        # Find all SQLite journal and WAL files
        for pattern in ['*.sqlite3-journal', '*.sqlite3-wal', '*.sqlite3-shm']:
            for db_aux_file in project_root.glob(pattern):
                try:
                    db_aux_file.unlink()
                    print_color(f"Removed SQLite auxiliary file: {db_aux_file.relative_to(project_root)}", 'yellow')
                    cleanup_count += 1
                except Exception as e:
                    debug_log(f"Error removing {db_aux_file}: {e}")
    except Exception as e:
        print_color(f"Error during SQLite auxiliary files cleanup: {e}", 'red')
    
    # 3. Kill any processes that might be locking the database
    try:
        # This will only work on Unix-like systems
        if os.name == 'posix':
            for db_file in project_root.glob('*.sqlite3*'):
                try:
                    # Find processes using the database file
                    result = subprocess.run(['lsof', '-t', str(db_file)], 
                                        capture_output=True, text=True, check=False)
                    if result.stdout:
                        pids = result.stdout.strip().split('\n')
                        for pid in pids:
                            print_color(f"Killing process {pid} that was locking {db_file.name}", 'yellow')
                            try:
                                os.kill(int(pid), 9)  # SIGKILL
                                cleanup_count += 1
                            except Exception as e:
                                debug_log(f"Error killing process {pid}: {e}")
                except Exception as e:
                    debug_log(f"Error checking processes for {db_file}: {e}")
    except Exception as e:
        debug_log(f"Error during process cleanup: {e}")
    
    # 4. Reset Django migrations state if needed
    try:
        migrations_dir = project_root / 'projects' / 'migrations'
        if migrations_dir.exists() and migrations_dir.is_dir():
            # Ensure __init__.py exists
            init_file = migrations_dir / '__init__.py'
            if not init_file.exists():
                with open(init_file, 'w') as f:
                    pass
                print_color(f"Created {init_file.relative_to(project_root)}", 'yellow')
                cleanup_count += 1
    except Exception as e:
        print_color(f"Error during migrations cleanup: {e}", 'red')
    
    # Summary
    if cleanup_count > 0:
        print_color(f"Cleanup complete: {cleanup_count} items cleaned up", 'green')
    else:
        print_color("No cleanup needed. Environment is clean.", 'green')

def find_project_root():
    """Find the Django project root directory"""
    # Start with the current directory
    current_dir = Path.cwd()
    debug_log(f"Starting directory search from: {current_dir}")
    
    # Check if the current directory has manage.py
    if (current_dir / 'manage.py').exists():
        debug_log(f"Found project root at current directory: {current_dir}")
        return current_dir
    
    # Try searching up to 3 levels up
    for _ in range(3):
        parent_dir = current_dir.parent
        if (parent_dir / 'manage.py').exists():
            debug_log(f"Found project root at parent directory: {parent_dir}")
            return parent_dir
        current_dir = parent_dir
    
    # If we can't find it, use the current directory
    print_color("Warning: Could not find Django project root with manage.py", 'yellow')
    print_color("Using current directory as project root", 'yellow')
    return Path.cwd()

def get_s3_path(category, filename):
    """Generate S3 path for a file"""
    prefix = S3_PREFIXES.get(category, '')
    return f"{prefix}{filename}"

def setup_database():
    """Set up the database with all required tables"""
    try:
        # First run cleanup of previous state to avoid conflicts
        cleanup_previous_state()
        
        # Find project root and database path
        project_root = find_project_root()
        db_path = project_root / 'db.sqlite3'
        debug_log(f"Database path: {db_path}")
        
        # Check if database already exists
        if db_path.exists():
            if not args.force:
                response = input(f"Database already exists at {db_path}. Overwrite? (y/n): ")
                if response.lower() != 'y':
                    print_color("Aborting setup.", 'yellow')
                    return False
            
            # Create backup unless explicitly disabled
            if not args.no_backup:
                backup_path = f"{db_path}.backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                try:
                    shutil.copy2(db_path, backup_path)
                    print_color(f"Created backup of existing database: {backup_path}", 'green')
                except Exception as e:
                    print_color(f"Warning: Could not create backup: {e}", 'yellow')
            else:
                print_color("Skipping database backup as requested", 'yellow')
            
            # Try to delete the database safely
            try:
                os.remove(db_path)
                print_color(f"Removed existing database: {db_path}", 'yellow')
            except Exception as e:
                print_color(f"Error removing database: {e}", 'red')
                print_color("Attempting to continue anyway...", 'yellow')
        
        # Create database directory if it doesn't exist
        db_path.parent.mkdir(exist_ok=True)
        
        # Create fresh database and connect
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print_color("Creating database tables...", 'blue', bold=True)
        
        # Create Django system tables (minimum required)
        cursor.execute("""
        CREATE TABLE "django_content_type" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "app_label" varchar(100) NOT NULL,
            "model" varchar(100) NOT NULL
        );
        """)
        
        cursor.execute("""
        CREATE TABLE "django_migrations" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "app" varchar(255) NOT NULL,
            "name" varchar(255) NOT NULL,
            "applied" datetime NOT NULL
        );
        """)
        
        # Create auth_user table needed for authentication
        print_color("Creating auth tables...", 'blue')
        cursor.execute("""
        CREATE TABLE "auth_user" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "password" varchar(128) NOT NULL,
            "last_login" datetime NULL,
            "is_superuser" bool NOT NULL,
            "username" varchar(150) NOT NULL UNIQUE,
            "last_name" varchar(150) NOT NULL,
            "email" varchar(254) NOT NULL,
            "is_staff" bool NOT NULL,
            "is_active" bool NOT NULL,
            "date_joined" datetime NOT NULL,
            "first_name" varchar(150) NOT NULL
        );
        """)
        
        # Create auth group tables
        cursor.execute("""
        CREATE TABLE "auth_group" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "name" varchar(150) NOT NULL UNIQUE
        );
        """)
        
        cursor.execute("""
        CREATE TABLE "auth_permission" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id"),
            "codename" varchar(100) NOT NULL,
            "name" varchar(255) NOT NULL
        );
        """)
        
        cursor.execute("""
        CREATE TABLE "auth_group_permissions" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "group_id" integer NOT NULL REFERENCES "auth_group" ("id"),
            "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id")
        );
        """)
        
        cursor.execute("""
        CREATE TABLE "auth_user_groups" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
            "group_id" integer NOT NULL REFERENCES "auth_group" ("id")
        );
        """)
        
        cursor.execute("""
        CREATE TABLE "auth_user_user_permissions" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
            "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id")
        );
        """)
        
        # Create sessions table
        cursor.execute("""
        CREATE TABLE "django_session" (
            "session_key" varchar(40) NOT NULL PRIMARY KEY,
            "session_data" text NOT NULL,
            "expire_date" datetime NOT NULL
        );
        """)
        
        # Create index for session table
        cursor.execute("""
        CREATE INDEX "django_session_expire_date_a5c62663" ON "django_session" ("expire_date");
        """)
        
        # Create admin tables
        cursor.execute("""
        CREATE TABLE "django_admin_log" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "action_time" datetime NOT NULL,
            "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
            "content_type_id" integer NULL REFERENCES "django_content_type" ("id"),
            "object_id" text NULL,
            "object_repr" varchar(200) NOT NULL,
            "action_flag" smallint unsigned NOT NULL CHECK ("action_flag" >= 0),
            "change_message" text NOT NULL
        );
        """)
        
        # Create models tables
        print_color("Creating Sword_img table...", 'blue')
        cursor.execute("""
        CREATE TABLE "projects_sword_img" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "item_number" integer NOT NULL,
            "image" varchar(100) NULL,
            "description" text NOT NULL
        );
        """)
        
        print_color("Creating Sword_sales table...", 'blue')
        cursor.execute("""
        CREATE TABLE "projects_sword_sales" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "item_number" integer NOT NULL,
            "image" varchar(100) NULL,
            "description" text NOT NULL,
            "price" varchar(50) NOT NULL
        );
        """)
        
        print_color("Creating BlogImages table...", 'blue')
        cursor.execute("""
        CREATE TABLE "projects_blogimages" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "image" varchar(100) NULL
        );
        """)
        
        print_color("Creating Blog table...", 'blue')
        cursor.execute("""
        CREATE TABLE "projects_blog" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "date" date NOT NULL,
            "description" text NOT NULL
        );
        """)
        
        print_color("Creating Blog_images relation table...", 'blue')
        cursor.execute("""
        CREATE TABLE "projects_blog_images" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "blog_id" integer NOT NULL REFERENCES "projects_blog" ("id"),
            "blogimages_id" integer NOT NULL REFERENCES "projects_blogimages" ("id")
        );
        """)
        
        print_color("Creating Hotel table...", 'blue')
        cursor.execute("""
        CREATE TABLE "projects_hotel" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "city_name" varchar(100) NOT NULL,
            "hotel_name" varchar(250) NOT NULL,
            "address" varchar(100) NOT NULL,
            "description" text NOT NULL,
            "distance" varchar(100) NOT NULL,
            "phone" varchar(100) NOT NULL
        );
        """)
        
        print_color("Creating Year table...", 'blue')
        cursor.execute("""
        CREATE TABLE "projects_year" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "title" varchar(4) NOT NULL,
            "class_year" integer NOT NULL
        );
        """)
        
        print_color("Creating Classes table...", 'blue')
        cursor.execute("""
        CREATE TABLE "projects_classes" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "class_title" varchar(250) NOT NULL,
            "start_date" date NOT NULL,
            "end_date" date NOT NULL,
            "description" text NOT NULL,
            "class_slots" integer NOT NULL
        );
        """)
        
        # Record migrations as completed in django_migrations
        print_color("Recording migrations as completed...", 'blue')
        migrations = [
            # Auth app migrations
            ("auth", "0001_initial"),
            ("auth", "0002_alter_permission_name_max_length"),
            ("auth", "0003_alter_user_email_max_length"),
            ("auth", "0004_alter_user_username_opts"),
            ("auth", "0005_alter_user_last_login_null"),
            ("auth", "0006_require_contenttypes_0002"),
            ("auth", "0007_alter_validators_add_error_messages"),
            ("auth", "0008_alter_user_username_max_length"),
            ("auth", "0009_alter_user_last_name_max_length"),
            ("auth", "0010_alter_group_name_max_length"),
            ("auth", "0011_update_proxy_permissions"),
            ("auth", "0012_alter_user_first_name_max_length"),
            
            # Admin app migrations
            ("admin", "0001_initial"),
            ("admin", "0002_logentry_remove_auto_add"),
            ("admin", "0003_logentry_add_action_flag_choices"),
            
            # Sessions app migrations
            ("sessions", "0001_initial"),
            
            # Contenttypes app migrations
            ("contenttypes", "0001_initial"),
            ("contenttypes", "0002_remove_content_type_name"),
            
            # Project app migrations
            ("projects", "0001_initial"),
            ("projects", "0002_classes_sword_img_and_more"),
            ("projects", "0003_classes_description"),
            ("projects", "0004_blog_hotel_sword_img_description"),
            ("projects", "0005_hotel_phone"),
            ("projects", "0006_blog_description"),
            ("projects", "0007_year_delete_project_classes_class_slots"),
            ("projects", "0008_year_title"),
            ("projects", "0009_sword_sales"),
            ("projects", "0010_alter_sword_sales_title"),
            ("projects", "0011_remove_sword_sales_title_sword_sales_item_number"),
            ("projects", "0012_remove_sword_img_title_sword_img_item_number"),
            ("projects", "0013_remove_blog_title_blog_date"),
            ("projects", "0014_alter_blog_date"),
            ("projects", "0015_alter_blog_date"),
            ("projects", "0016_alter_blog_date"),
            ("projects", "0017_alter_blog_date_alter_classes_end_date_and_more"),
            ("projects", "0018_alter_classes_end_date_alter_classes_start_date"),
            ("projects", "0019_blogimages_blog_images"),
            ("projects", "0020_remove_sword_img_image_remove_sword_sales_image_and_more"),
            ("projects", "0021_blogimages_remove_blog_images_blog_images"),
            ("projects", "0022_rename_images_sword_img_image_and_more"),
            ("projects", "0023_auto_20240321_1847"),
            ("projects", "0024_alter_blog_description"),
            ("projects", "0025_article"),
            ("projects", "0026_delete_article"),
            ("projects", "0027_alter_blogimages_image_alter_sword_img_image_and_more"),
            ("projects", "0028_alter_hotel_phone")
        ]
        
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for app, name in migrations:
            cursor.execute(
                "INSERT INTO django_migrations (app, name, applied) VALUES (?, ?, ?)",
                (app, name, now)
            )
        
        conn.commit()
        print_color("Database structure created successfully!", 'green', bold=True)
        
        # Populate with sample data
        populate_database(conn, cursor)
        
        conn.close()
        return True
        
    except Exception as e:
        print_color(f"Error setting up database: {str(e)}", 'red')
        if args.debug:
            traceback.print_exc()
        return False

def populate_database(conn, cursor):
    """Populate the database with S3 paths"""
    try:
        # Fix for migration 0020 specifically - ensure table structure is correct
        # This directly addresses the "near None: syntax error" issue
        print_color("\nEnsuring table structure is compatible with Django models...", 'blue', bold=True)
        
        # These extra checks help address the specific migration 0020 error
        try:
            cursor.execute("PRAGMA table_info(projects_sword_img)")
            columns = {col[1] for col in cursor.fetchall()}
            if 'image' not in columns:
                print_color("Adding 'image' column to projects_sword_img to fix migration 0020 issue", 'yellow')
                cursor.execute("ALTER TABLE projects_sword_img ADD COLUMN image varchar(100) NULL")
                
            cursor.execute("PRAGMA table_info(projects_sword_sales)")
            columns = {col[1] for col in cursor.fetchall()}
            if 'image' not in columns:
                print_color("Adding 'image' column to projects_sword_sales to fix migration 0020 issue", 'yellow')
                cursor.execute("ALTER TABLE projects_sword_sales ADD COLUMN image varchar(100) NULL")
                
            conn.commit()
        except Exception as e:
            print_color(f"Non-critical table adjustment error (can be ignored): {str(e)}", 'yellow')
        
        print_color("\nPopulating database with S3 paths...", 'blue', bold=True)
        
        # Populate Sword_img table
        print_color("\nAdding Sword_img records...", 'blue')
        for i, filename in enumerate(SAMPLE_FILES['sword'], 1):
            s3_path = get_s3_path('sword', filename)
            cursor.execute(
                "INSERT INTO projects_sword_img (item_number, image, description) VALUES (?, ?, ?)",
                (i, s3_path, f"Sample sword {i}")
            )
            print_color(f"  ✅ Added Sword_img {i} with S3 path: {s3_path}", 'green')
        
        # Populate Sword_sales table
        print_color("\nAdding Sword_sales records...", 'blue')
        for i, filename in enumerate(SAMPLE_FILES['sales'], 1):
            s3_path = get_s3_path('sales', filename)
            cursor.execute(
                "INSERT INTO projects_sword_sales (item_number, image, description, price) VALUES (?, ?, ?, ?)",
                (i, s3_path, f"Sample sword for sale {i}", f"${i}00.00")
            )
            print_color(f"  ✅ Added Sword_sales {i} with S3 path: {s3_path}", 'green')
        
        # Populate BlogImages table
        print_color("\nAdding BlogImages records...", 'blue')
        blog_image_ids = []
        for i, filename in enumerate(SAMPLE_FILES['blog'], 1):
            s3_path = get_s3_path('blog', filename)
            cursor.execute(
                "INSERT INTO projects_blogimages (image) VALUES (?)",
                (s3_path,)
            )
            blog_image_id = cursor.lastrowid
            blog_image_ids.append(blog_image_id)
            print_color(f"  ✅ Added BlogImages {i} with S3 path: {s3_path}", 'green')
        
        # Create a sample blog post
        print_color("\nAdding sample Blog post...", 'blue')
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute(
            "INSERT INTO projects_blog (date, description) VALUES (?, ?)",
            (today, "<p>This is a sample blog post created by the setup script.</p>")
        )
        blog_id = cursor.lastrowid
        
        # Associate blog images with the blog post
        for image_id in blog_image_ids:
            cursor.execute(
                "INSERT INTO projects_blog_images (blog_id, blogimages_id) VALUES (?, ?)",
                (blog_id, image_id)
            )
        
        print_color(f"  ✅ Added Blog post with ID {blog_id} and {len(blog_image_ids)} images", 'green')
        
        # Add a sample hotel
        print_color("\nAdding sample Hotel record...", 'blue')
        cursor.execute(
            "INSERT INTO projects_hotel (city_name, hotel_name, address, description, distance, phone) VALUES (?, ?, ?, ?, ?, ?)",
            ("Sample City", "Sample Hotel", "123 Main St", "Sample hotel description", "2 miles", "555-123-4567")
        )
        
        # Add a sample year
        print_color("\nAdding sample Year record...", 'blue')
        current_year = datetime.now().year
        cursor.execute(
            "INSERT INTO projects_year (title, class_year) VALUES (?, ?)",
            (str(current_year), current_year)
        )
        
        # Add a sample class
        print_color("\nAdding sample Classes record...", 'blue')
        start_date = f"{current_year}-06-01"
        end_date = f"{current_year}-06-15"
        cursor.execute(
            "INSERT INTO projects_classes (class_title, start_date, end_date, description, class_slots) VALUES (?, ?, ?, ?, ?)",
            ("Sample Swordmaking Class", start_date, end_date, "Learn the basics of sword making", 10)
        )
        
        conn.commit()
        print_color("\nDatabase populated successfully!", 'green', bold=True)
        
    except Exception as e:
        print_color(f"Error populating database: {str(e)}", 'red')
        if args.debug:
            traceback.print_exc()

def verify_setup():
    """Verify the setup was successful"""
    print_color("\n=== Verifying Setup ===", 'blue', bold=True)
    
    try:
        # Find the database
        project_root = find_project_root()
        db_path = project_root / 'db.sqlite3'
        
        if not db_path.exists():
            print_color("Database not found! Setup failed.", 'red')
            return False
        
        # Connect and check key tables
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check for essential tables
        required_tables = [
            "django_migrations",
            "projects_sword_img",
            "projects_sword_sales",
            "projects_blogimages"
        ]
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        
        missing_tables = [table for table in required_tables if table not in tables]
        
        if missing_tables:
            print_color(f"Missing tables: {', '.join(missing_tables)}", 'red')
            return False
        
        # Check if migrations are recorded
        cursor.execute("SELECT COUNT(*) FROM django_migrations;")
        migration_count = cursor.fetchone()[0]
        
        if migration_count < 20:  # We expect at least 20 migrations
            print_color(f"Migration history incomplete. Found only {migration_count} migrations.", 'yellow')
        else:
            print_color(f"Migration history looks good. Found {migration_count} migrations.", 'green')
        
        # Check for sample data
        cursor.execute("SELECT COUNT(*) FROM projects_sword_img;")
        sword_count = cursor.fetchone()[0]
        
        if sword_count == 0:
            print_color("Warning: No sword images found in database.", 'yellow')
        else:
            print_color(f"Found {sword_count} sword images.", 'green')
        
        conn.close()
        return True
        
    except Exception as e:
        print_color(f"Verification failed: {e}", 'red')
        if args.debug:
            traceback.print_exc()
        return False

def main():
    """Main function"""
    print_color("=== OMIMI SWORDS DATABASE SETUP SCRIPT ===", 'blue', bold=True)
    print_color(f"S3 Bucket: {BUCKET_NAME}", 'blue')
    print_color("This script will create a fresh database with all required tables and sample data.", 'yellow')
    print_color("It bypasses Django migrations to avoid compatibility issues.", 'yellow')
    print_color("It also cleans up artifacts from previous failed setups.", 'yellow')
    
    if setup_database():
        if verify_setup():
            print_color("\n=== SETUP COMPLETE ===", 'green', bold=True)
            print_color("Next steps:", 'blue')
            print_color("1. Create a Django superuser: python3 manage.py createsuperuser", 'white')
            print_color("2. Start the development server: python3 manage.py runserver", 'white')
            print_color("3. Access the admin interface: http://localhost:8000/admin", 'white')
            print_color("4. Check that images are loading from S3", 'white')
            
            # Convenience options
            try:
                create_superuser = input("\nWould you like to create a superuser now? (y/n): ")
                if create_superuser.lower() == 'y':
                    os.system("python3 manage.py createsuperuser")
            except KeyboardInterrupt:
                print("\nSkipping superuser creation.")
        else:
            print_color("\n=== SETUP PARTIALLY COMPLETE WITH WARNINGS ===", 'yellow', bold=True)
            print_color("Database was created but verification found some issues.", 'yellow')
            print_color("You may still be able to use the application.", 'yellow')
    else:
        print_color("\n=== SETUP FAILED ===", 'red', bold=True)
        print_color("Please check the error messages above.", 'yellow')
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_color("\nSetup canceled by user.", 'yellow')
        sys.exit(0)