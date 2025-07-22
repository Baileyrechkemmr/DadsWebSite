from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    location = 'static'
    file_overwrite = True  # Allow overwriting for updates
    # Disable query string auth for static files - they should be public
    querystring_auth = False
    # Remove ACL - bucket doesn't support ACLs (modern S3 security)
    default_acl = None
    # Ensure static files are publicly accessible via bucket policy
    custom_domain = None  # Use S3 direct URLs


class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False
    # Keep query string auth for media files (they might be private)
    querystring_auth = True
    # Set default ACL to None (use bucket default)
    default_acl = None
