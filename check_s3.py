import boto3
import os
import environ

try:
    # Load environment variables
    env = environ.Env()
    environ.Env.read_env('.env')
    
    # Get AWS credentials from environment
    access_key = env('AWS_ACCESS_KEY_ID')
    secret_key = env('AWS_SECRET_ACCESS_KEY')
    region = env('AWS_S3_REGION', default='us-east-1')
    bucket_name = env('AWS_STORAGE_BUCKET_NAME')
    
    # Print info (without showing secrets)
    print(f"AWS Access Key ID: {access_key[:5]}...")
    print(f"AWS Secret Access Key: {secret_key[:3]}...")
    print(f"AWS Region: {region}")
    print(f"S3 Bucket: {bucket_name}")
    
    # Create S3 client
    s3 = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )
    
    # Test bucket access
    print("\nTesting bucket access...")
    response = s3.head_bucket(Bucket=bucket_name)
    print("✓ Bucket exists and credentials have access")
    
    # List a few objects in the bucket
    print("\nListing some objects in the bucket:")
    response = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=5)
    if 'Contents' in response:
        for obj in response['Contents']:
            print(f"- {obj['Key']} ({obj['Size']} bytes)")
    else:
        print("No objects found in the bucket")
    
    # Try to get a specific object (the one that's failing)
    print("\nTesting specific object access:")
    try:
        obj_key = 'static/dadsBanerOne.jpeg'
        print(f"Attempting to access: {obj_key}")
        response = s3.head_object(Bucket=bucket_name, Key=obj_key)
        print(f"✓ Object exists and is accessible ({response['ContentLength']} bytes)")
        print(f"  Content Type: {response.get('ContentType')}")
    except Exception as e:
        print(f"✗ Error accessing object: {str(e)}")
    
    # Test public URL access
    print("\nGenerating pre-signed URL for testing:")
    try:
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': obj_key},
            ExpiresIn=3600
        )
        print(f"URL: {url}")
        print("To test: curl -I '{url}'")
    except Exception as e:
        print(f"✗ Error generating URL: {str(e)}")
        
except Exception as e:
    print(f"Error: {str(e)}")