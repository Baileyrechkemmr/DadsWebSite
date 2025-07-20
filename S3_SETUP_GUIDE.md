# S3 Storage Setup Guide for Cross-Platform Django

This guide explains how to configure and maintain S3 storage for your Django project across all environments (macOS, Linux, Windows, and WSL).

## Overview of Changes

The following changes have been implemented to ensure cross-platform compatibility:

1. **Settings Updates**:
   - Enabled `AWS_S3_ENDPOINT_URL` for WSL compatibility
   - Enabled `STATICFILES_STORAGE` to use S3 for static files

2. **Model Updates**:
   - Fixed `BlogImages` model to use `upload_to='images/'` instead of `static/`
   - Created migration to update the database schema

3. **Migration Tools**:
   - Created scripts to migrate existing files and ensure compatibility

## Setup Instructions

### Option 1: Automated Setup

For a complete automated setup, run:

```bash
python setup_s3_storage.py
```

This script will:
- Check your environment configuration
- Apply database migrations
- Collect static files and upload to S3
- Migrate blog images from static/ to images/ directory

### Option 2: Manual Setup

If you prefer to do the setup manually, follow these steps:

1. **Apply Database Migrations**:
   ```bash
   python manage.py migrate
   ```

2. **Collect Static Files**:
   ```bash
   python collect_static_to_s3.py
   ```

3. **Migrate Blog Images**:
   ```bash
   python migrate_blog_images.py
   ```

## Testing Your Setup

To verify your setup is working correctly:

1. **Check WSL-specific configuration**:
   ```bash
   python check_s3_wsl.py
   ```

2. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

3. **Open your browser** and check if images are loading correctly

## Troubleshooting

### Images Not Loading in WSL

If images still aren't loading in WSL:

1. Verify that `AWS_S3_ENDPOINT_URL = 'https://s3.amazonaws.com'` is uncommented in settings.py
2. Run `python check_s3_wsl.py` to diagnose connectivity issues
3. Check if the database migration was applied successfully
4. Verify that static files were uploaded to S3 correctly

### Cross-Platform File Path Issues

If you encounter file path issues between platforms:

1. Ensure all image uploads use relative paths
2. Avoid hardcoding path separators (use `os.path.join` instead)
3. Use forward slashes in template URLs (`/media/image.jpg` not `\media\image.jpg`)

## Maintenance

### Adding New Images

All new images uploaded through the BlogImages model will automatically go to the correct S3 location (images/ directory).

### Updating Static Files

Whenever you update static files, run the collectstatic command:

```bash
python collect_static_to_s3.py
```

### Backing Up S3 Data

Periodically back up your S3 bucket data using the AWS CLI:

```bash
aws s3 sync s3://your-bucket-name/ ./backup-folder/
```

## Additional Resources

- [Django S3 Storage Documentation](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html)
- [AWS S3 Troubleshooting Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/troubleshooting.html)
- [WSL Networking Documentation](https://docs.microsoft.com/en-us/windows/wsl/networking)