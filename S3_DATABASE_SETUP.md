# S3 Database Setup Guide

## Overview

This guide explains how to set up and populate your local Django SQLite database with S3 paths for the Omimi Swords website. This configuration allows your website to fetch images from S3 storage without requiring you to upload files through Django's admin interface.

## Prerequisites

1. Python 3.6+ installed
2. Django project configured (omimi_swords)
3. AWS credentials set up in your `.env` file:
   ```
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_STORAGE_BUCKET_NAME=ominisword-images
   AWS_S3_REGION=us-east-1
   ```
4. S3 bucket with the correct structure (created and populated with images)

## S3 Path Structure

The script uses the following path structure in S3:

```
├── gallery/
│   ├── swords/
│   │   ├── sword_one.webp
│   │   ├── 14.jpg
│   │   └── cef.jpg
│   └── sales/
│       ├── sale_item_1.jpg
│       ├── sale_item_2.jpg
│       └── sale_item_3.jpg
├── blog/
│   └── 2024/
│       └── 12/
│           ├── 100_3589.png
│           ├── 100_4278.png
│           └── blog_image_1.jpg
└── static/
    └── ui/
        ├── blog.png
        ├── dadsBanerOne.jpeg
        └── howard1.jpeg
```

## How to Use the Script

1. Ensure your virtual environment is activated (if you're using one)

2. Run the population script:
   ```bash
   # Standard usage
   python3 populate_s3_paths.py
   
   # If you get "already exists" errors
   python3 populate_s3_paths.py --skip-migrations
   
   # For database corruption ("near None: syntax error")
   python3 populate_s3_paths.py --direct-mode
   
   # To start completely fresh
   python3 populate_s3_paths.py --fresh-db
   
   # Debug mode with detailed error messages
   python3 populate_s3_paths.py --debug
   ```

3. The script will:
   - Connect to your Django database
   - Update or create records in Sword_img, Sword_sales, and BlogImages models
   - Point image fields to the appropriate S3 paths
   - Associate blog images with blog posts
   - Display a summary of what was updated

## What the Script Does

The script updates three main model types:

1. **Sword_img**: Updates image paths to point to `gallery/swords/` in S3
2. **Sword_sales**: Updates image paths to point to `gallery/sales/` in S3
3. **BlogImages**: Updates image paths to point to `blog/2024/12/` in S3

If no records exist in the database, the script will create sample records using predefined sample filenames.

## Sample Files

The script includes sample filenames for each category. If your actual files in S3 have different names, you can modify the `SAMPLE_FILES` dictionary in the script.

## Troubleshooting

### Common Issues

1. **"near None: syntax error"**:
   - This is a SQLite error that usually means your database is corrupted or incompatible
   - Use the robust direct mode to bypass Django's ORM:
     ```bash
     python3 populate_s3_paths.py --direct-mode
     ```
   - Or delete and recreate the database:
     ```bash
     python3 populate_s3_paths.py --fresh-db
     ```

2. **"project_classes already exists" error**:
   - This means migrations are failing because tables already exist
   - Skip migrations and try direct mode:
     ```bash
     python3 populate_s3_paths.py --skip-migrations --direct-mode
     ```

3. **Images not displaying**: 
   - Check if the S3 paths in the database match the actual paths in your S3 bucket
   - Verify AWS credentials in your `.env` file
   - Ensure Django's S3 storage settings are correctly configured

4. **Permission errors**:
   - Verify your AWS user has proper permissions to access the S3 bucket

5. **404 Not Found errors**:
   - The S3 path might be incorrect or the file doesn't exist at that location
   - Use the AWS Console to verify the file exists at the expected path

6. **Debug Mode**:
   - Get detailed error messages with:
     ```bash
     python3 populate_s3_paths.py --debug
     ```

### Database Inspection

You can check the paths stored in your database using Django's shell:

```python
# Start Django shell
python3 manage.py shell

# In the shell
from projects.models import Sword_img, Sword_sales, BlogImages
print(Sword_img.objects.all().values_list('item_number', 'image'))
print(Sword_sales.objects.all().values_list('item_number', 'image'))
print(BlogImages.objects.all().values_list('id', 'image'))
```

## After Running the Script

1. Start your Django development server:
   ```bash
   python3 manage.py runserver
   ```

2. Visit your website and check if the images are loading from S3

3. If there are issues, check the browser console for 404 errors or other issues

## Additional Resources

- Check `S3_ARCHITECTURE_PLAN.md` for the complete S3 architecture design
- Review `omimi/settings.py` to ensure S3 storage is properly configured
- Use `check_s3_files.py` to verify your S3 bucket contents