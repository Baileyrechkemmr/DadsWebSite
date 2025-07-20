# S3 Implementation Testing Checklist

Use this checklist to verify that the S3 storage solution is working correctly across all environments.

## Environment Setup Verification

- [ ] `.env` file contains all required AWS credentials:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_STORAGE_BUCKET_NAME`
  - `AWS_S3_REGION`
  - `USE_S3=True`

- [ ] Django settings are properly configured:
  - `AWS_S3_ENDPOINT_URL` is uncommented
  - `STATICFILES_STORAGE` is set to use S3
  - `DEFAULT_FILE_STORAGE` is set to use S3

## Database Migration Verification

- [ ] Run `python manage.py showmigrations projects` to verify migration `0029_alter_blogimages_image` is applied
- [ ] Check that BlogImages model uses `upload_to='images/'` in Django admin

## S3 Connection Testing

- [ ] Run `python check_s3_wsl.py` to verify S3 connectivity
- [ ] Verify bucket access and permissions are correct
- [ ] Test URL styles to ensure all are accessible

## Static Files Verification

1. Check Static Files in S3:
   - [ ] CSS files are accessible
   - [ ] JavaScript files are accessible
   - [ ] Image files are accessible

2. Run Development Server:
   - [ ] Static files load without 404 errors
   - [ ] CSS styles are applied correctly
   - [ ] JavaScript functionality works

## Media Files Verification

1. Existing Media Files:
   - [ ] Blog images load correctly
   - [ ] Sword images load correctly
   - [ ] Sales images load correctly

2. Upload New Media File:
   - [ ] Upload new image through admin interface
   - [ ] Verify file is uploaded to S3 (images/ directory)
   - [ ] Verify file is accessible on the website

## Cross-Platform Testing

1. macOS Testing:
   - [ ] Static files load correctly
   - [ ] Media files load correctly
   - [ ] File uploads work

2. WSL Testing:
   - [ ] Static files load correctly
   - [ ] Media files load correctly
   - [ ] File uploads work

3. Windows/Linux Testing (if applicable):
   - [ ] Static files load correctly
   - [ ] Media files load correctly
   - [ ] File uploads work

## Performance Testing

- [ ] Page load time is acceptable
- [ ] Image load time is reasonable
- [ ] Multiple simultaneous uploads work correctly

## Error Handling Testing

- [ ] Site handles S3 temporary unavailability gracefully
- [ ] Invalid file uploads are rejected appropriately
- [ ] Error messages are clear and helpful

## Security Testing

- [ ] S3 bucket has appropriate access controls
- [ ] Files are not publicly accessible unless intended
- [ ] URLs use HTTPS

## Deployment Verification

- [ ] Run `python setup_s3_storage.py` to verify automated deployment works
- [ ] Verify all tests pass after automated deployment

## Notes

Use this section to document any issues encountered during testing and their resolutions:

- Issue 1: [Description]
  - Resolution: [Steps taken]

- Issue 2: [Description]
  - Resolution: [Steps taken]
