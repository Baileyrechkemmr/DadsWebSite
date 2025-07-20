# Omimi Swords Environment Setup Guide

This guide provides instructions for setting up your development environment for the Omimi Swords project across different platforms.

## Prerequisites

### Required Software

- Python 3.8+
- Git
- Virtual Environment (venv, virtualenv, or conda)

### Required Accounts

- AWS Account with S3 access

## Basic Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Baileyrechkemmr/DadsWebSite.git
cd DadsWebSite
```

### 2. Create a Virtual Environment

```bash
# Using venv (Python 3)
python -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate

# Activate on WSL (if using Windows' Python)
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Environment Configuration

### 1. Create .env File

Create a `.env` file in the project root with the following variables:

```
# Django Settings
SECRET_KEY=your_django_secret_key
DEBUG=True

# Email Configuration
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_email_password

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_STORAGE_BUCKET_NAME=your_bucket_name
AWS_S3_REGION=us-east-1  # Change as needed
USE_S3=True

# AWS DynamoDB Configuration (if using AWS blog feature)
DYNAMODB_BLOG_TABLE=your_dynamodb_table_name
```

### 2. S3 Bucket Setup

Ensure your S3 bucket has the following:

1. **Proper Permissions**:
   - Allow read access for static/media files
   - Allow write access for your AWS user

2. **CORS Configuration** (if needed):
   ```json
   {
     "CORSRules": [
       {
         "AllowedOrigins": ["*"],  // Restrict to your domain in production
         "AllowedMethods": ["GET"],
         "MaxAgeSeconds": 3000,
         "AllowedHeaders": ["*"]
       }
     ]
   }
   ```

## Database Setup

### 1. Apply Migrations

```bash
python manage.py migrate
```

### 2. Create Superuser

```bash
python manage.py createsuperuser
```

## Platform-Specific Setup

### Windows Subsystem for Linux (WSL)

When using WSL, ensure:

1. AWS S3 endpoint URL is enabled in settings.py:
   ```python
   AWS_S3_ENDPOINT_URL = 'https://s3.amazonaws.com'
   ```

2. Run the WSL compatibility check:
   ```bash
   python check_s3_wsl.py
   ```

3. If experiencing path issues, ensure file paths use forward slashes.

### macOS

No special configuration needed beyond the standard setup.

### Linux

No special configuration needed beyond the standard setup.

## Finalizing Setup

### 1. Collect Static Files

```bash
python collect_static_to_s3.py
```

### 2. Migrate Blog Images

```bash
python migrate_blog_images.py
```

### 3. Run Development Server

```bash
python manage.py runserver
```

## Troubleshooting

### Environment Variables Not Loading

- Verify the `.env` file exists in the project root
- Check that `django-environ` is installed
- Ensure the environment is properly activated

### S3 Connection Issues

- Verify AWS credentials are correct
- Check S3 bucket permissions
- Run `python check_s3_wsl.py` for diagnostics

### Database Migration Issues

- If migrations fail, try `python manage.py migrate --fake-initial`
- For stubborn migration issues, consult `MIGRATION_GUIDE.md`

## Additional Resources

- For S3 configuration details, see `S3_SETUP_GUIDE.md`
- For deployment instructions, see `DEPLOYMENT_INSTRUCTIONS.md`
- For testing procedures, see `S3_TESTING_CHECKLIST.md`
