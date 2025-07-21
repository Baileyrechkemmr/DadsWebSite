from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    location = 'static'
    file_overwrite = False
    # Disable query string auth for static files - they should be public
    querystring_auth = False
    # Don't set ACL - use bucket default (modern S3 buckets have ACLs disabled)
    default_acl = None


class MediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False
    # Keep query string auth for media files (they might be private)
    querystring_auth = True
    # Don't set ACL - use bucket default (modern S3 buckets have ACLs disabled)
    default_acl = None
