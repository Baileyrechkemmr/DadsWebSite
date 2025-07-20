import boto3
import environ
from urllib.parse import urlparse
from botocore.exceptions import ClientError

# Load environment variables
env = environ.Env()
environ.Env.read_env('.env')

ACCESS_KEY = env('AWS_ACCESS_KEY_ID')
SECRET_KEY = env('AWS_SECRET_ACCESS_KEY')
REGION = env('AWS_S3_REGION', default='us-east-1')
BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')

# Create S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION
)

# Function to test direct S3 access
def test_direct_access(key):
    try:
        response = s3.head_object(Bucket=BUCKET_NAME, Key=key)
        print(f"✓ Direct S3 API access successful for '{key}'")
        return True
    except ClientError as e:
        print(f"✗ Direct S3 API access failed for '{key}': {e}")
        return False

# Function to check bucket CORS configuration
def check_cors():
    try:
        cors = s3.get_bucket_cors(Bucket=BUCKET_NAME)
        print("Current CORS Configuration:")
        print(cors)
        return cors
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchCORSConfiguration':
            print("✗ No CORS configuration found on bucket")
        else:
            print(f"✗ Error checking CORS: {e}")
        return None

# Function to set CORS configuration
def set_cors():
    cors_config = {
        'CORSRules': [
            {
                'AllowedOrigins': ['*'],  # For development, use * 
                'AllowedMethods': ['GET', 'HEAD'],
                'AllowedHeaders': ['*'],
                'MaxAgeSeconds': 3000
            }
        ]
    }
    
    try:
        s3.put_bucket_cors(Bucket=BUCKET_NAME, CORSConfiguration=cors_config)
        print("✓ CORS configuration set successfully")
        return True
    except ClientError as e:
        print(f"✗ Error setting CORS: {e}")
        return False

# Function to check public access settings
def check_public_access():
    try:
        response = s3.get_public_access_block(Bucket=BUCKET_NAME)
        print("Public Access Settings:")
        print(response['PublicAccessBlockConfiguration'])
        return response['PublicAccessBlockConfiguration']
    except ClientError as e:
        print(f"✗ Error checking public access settings: {e}")
        return None

# Function to make objects public if needed
def make_objects_public(prefix="static/"):
    try:
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=BUCKET_NAME, Prefix=prefix)
        
        for page in pages:
            if 'Contents' not in page:
                continue
                
            for obj in page['Contents']:
                key = obj['Key']
                try:
                    s3.put_object_acl(Bucket=BUCKET_NAME, Key=key, ACL='public-read')
                    print(f"✓ Made '{key}' public")
                except ClientError as e:
                    print(f"✗ Error setting ACL on '{key}': {e}")
        
        return True
    except ClientError as e:
        print(f"✗ Error making objects public: {e}")
        return False

# Function to test a presigned URL
def test_presigned_url(key):
    try:
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': key},
            ExpiresIn=3600
        )
        print(f"Presigned URL: {url}")
        print("To test: curl -I '{url}'")
        return url
    except ClientError as e:
        print(f"✗ Error generating presigned URL: {e}")
        return None

# Function to generate direct URL (if public)
def get_direct_url(key):
    return f"https://{BUCKET_NAME}.s3.amazonaws.com/{key}"

# Main function
def main():
    print(f"Testing S3 access for bucket: {BUCKET_NAME}")
    print("="*80)
    
    # Test keys
    test_keys = ['static/dadsBanerOne.jpeg', 'static/howard1.jpeg']
    
    # Check direct access for each key
    print("\nDirect Access Check:")
    for key in test_keys:
        test_direct_access(key)
    
    # Check CORS configuration
    print("\nCORS Configuration:")
    cors_config = check_cors()
    
    # Check public access settings
    print("\nPublic Access Settings:")
    public_access = check_public_access()
    
    # If public access is blocked at bucket level and we can't set CORS
    if public_access and (public_access.get('BlockPublicAcls', False) or 
                           public_access.get('BlockPublicPolicy', False)):
        print("\n⚠️  Bucket has public access blocked. Options:")
        print("1. Use presigned URLs (which should work with proper CORS)")
        print("2. Update bucket policy in AWS Console to allow public access")
    
    # Ask to apply fixes
    print("\nPossible Solutions:")
    print("1. Set CORS configuration")
    print("2. Make objects public (if not blocked by bucket settings)")
    print("3. Test presigned URLs")
    print("4. Exit without changes")
    
    choice = input("\nChoose an action (1-4): ")
    
    if choice == "1":
        set_cors()
    elif choice == "2":
        prefix = input("Prefix to make public (default 'static/'): ") or "static/"
        make_objects_public(prefix)
    elif choice == "3":
        for key in test_keys:
            test_presigned_url(key)
    
    print("\nDone")

if __name__ == "__main__":
    main()