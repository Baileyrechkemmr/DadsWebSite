from storages.backends.s3boto3 import S3Boto3Storage


class S3StaticStorage(S3Boto3Storage):
    """Custom S3 storage for static files"""
    location = 'static'  # This tells Django that static files are in the 'static/' folder in S3
    default_acl = 'public-read'
    querystring_auth = False  # Don't use signed URLs for static files