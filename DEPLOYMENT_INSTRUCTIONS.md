# Deployment Instructions for Cross-Platform S3 Solution

This guide provides step-by-step instructions for deploying the S3 storage solution across different environments (macOS, Linux, Windows, WSL).

## Prerequisites

Before starting the deployment, ensure you have:

1. **AWS Credentials** set up in your `.env` file:
   ```
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_STORAGE_BUCKET_NAME=your_bucket_name
   AWS_S3_REGION=your_region
   USE_S3=True
   ```

2. **Required Python Packages**:
   ```
   django-storages
   boto3
   django-environ
   requests
   ```

## Deployment Steps

### Option 1: Automated Deployment (Recommended)

The automated script handles all the necessary steps for deploying the S3 solution:

```bash
# Run the comprehensive setup script
python setup_s3_storage.py
```

This script will:
- Verify your environment configuration
- Apply database migrations
- Collect static files and upload them to S3
- Migrate blog images from static/ to images/ directory

### Option 2: Manual Deployment

If you prefer to run the deployment steps individually:

1. **Apply Database Migrations**:
   ```bash
   python manage.py migrate
   ```

2. **Upload Static Files to S3**:
   ```bash
   python collect_static_to_s3.py
   ```

3. **Migrate Blog Images**:
   ```bash
   python migrate_blog_images.py
   ```

## WSL-Specific Setup

For Windows Subsystem for Linux (WSL) environments:

1. **Verify WSL Compatibility**:
   ```bash
   python check_s3_wsl.py
   ```

2. **Troubleshoot WSL Issues**:
   - Ensure `AWS_S3_ENDPOINT_URL` is properly set in `settings.py`
   - Check network connectivity to S3 endpoints
   - Verify file paths are using forward slashes

## Verifying the Deployment

### 1. Start the Development Server

```bash
python manage.py runserver
```

### 2. Test Image Loading

Visit the following URLs in your browser:

- Blog page: http://127.0.0.1:8000/blog/
- Image gallery: http://127.0.0.1:8000/gallery/

All images should load correctly without 404 errors.

### 3. Test File Uploads

1. Log in to the admin panel: http://127.0.0.1:8000/admin/
2. Upload a new image through the BlogImages model
3. Verify it appears correctly on the site

## Troubleshooting

### Common Issues and Solutions

#### 1. Images Not Loading

- **Issue**: 404 errors when accessing images
- **Solution**: 
  - Run `python check_s3_wsl.py` to diagnose connectivity issues
  - Verify S3 bucket permissions
  - Check that the migration script ran successfully

#### 2. File Upload Errors

- **Issue**: Cannot upload new files
- **Solution**: 
  - Check S3 write permissions
  - Verify AWS credentials are correct
  - Ensure `DEFAULT_FILE_STORAGE` is correctly set

#### 3. Static Files Not Found

- **Issue**: CSS/JS files not loading
- **Solution**: 
  - Run `python collect_static_to_s3.py` again
  - Check browser console for specific error messages
  - Verify `STATICFILES_STORAGE` setting is enabled

## Production Considerations

### 1. Environment Variables

Ensure production environment variables are securely configured and not hardcoded.

### 2. CORS Configuration

If serving assets from a different domain, set up CORS in your S3 bucket:

```json
{
  "CORSRules": [
    {
      "AllowedOrigins": ["https://your-production-domain.com"],
      "AllowedMethods": ["GET"],
      "MaxAgeSeconds": 3000,
      "AllowedHeaders": ["*"]
    }
  ]
}
```

### 3. Regular Backups

Schedule regular backups of your S3 bucket:

```bash
aws s3 sync s3://your-bucket-name/ ./backup-folder/
```

## Additional Resources

- For detailed S3 configuration options, see `S3_SETUP_GUIDE.md`
- For AWS blog service implementation, see `AWS_BLOG_SETUP.md`