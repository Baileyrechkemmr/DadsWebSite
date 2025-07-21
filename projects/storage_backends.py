from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    location = 'static'
    file_overwrite = False
    # Disable query string auth for static files - they should be public
    querystring_auth = False
    # Set public-read ACL for static files
    default_acl = 'public-read'
    # Custom domain will be set in __init__ to avoid pre-signed URLs

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure we use the bucket name from settings
        from django.conf import settings
        self.custom_domain = f'{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'


class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False
    # Keep query string auth for media files (they might be private)
    querystring_auth = True