# AWS Setup Instructions for Omimi Swords S3 Migration

## What the AWS Account Admin Needs to Do

### Step 1: Create S3 Bucket
```
Bucket Name: omimi-media-bucket
Region: us-east-1 (or your preferred region)
Public Access: Allow public read for images
Versioning: Enabled (recommended for backup)
```

**AWS Console Steps:**
1. Go to S3 in AWS Console
2. Click "Create bucket"
3. Name: `omimi-media-bucket`
4. Region: `us-east-1`
5. **Uncheck "Block all public access"** (we need public read for images)
6. Acknowledge the warning about public access
7. Enable versioning
8. Click "Create bucket"

### Step 2: Create IAM User for Django App
```
User Name: omimi-django-user
Access Type: Programmatic access (API keys)
Permissions: S3 full access to omimi-media-bucket only
```

**IAM Console Steps:**
1. Go to IAM → Users → Create User
2. Username: `omimi-django-user`
3. Select "Programmatic access"
4. Permissions: "Attach policies directly"
5. Create and attach this custom policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::omimi-media-bucket",
                "arn:aws:s3:::omimi-media-bucket/*"
            ]
        }
    ]
}
```

6. Complete user creation
7. **SAVE THE ACCESS KEY ID AND SECRET ACCESS KEY** - you'll need these!

### Step 3: Configure Bucket Policy for Public Read
In the S3 bucket, add this bucket policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::omimi-media-bucket/*"
        }
    ]
}
```

### Step 4: Provide These Credentials to Developer

**Environment Variables Needed:**
```
AWS_ACCESS_KEY_ID=AKIA... (from Step 2)
AWS_SECRET_ACCESS_KEY=... (from Step 2) 
AWS_STORAGE_BUCKET_NAME=omimi-media-bucket
AWS_S3_REGION_NAME=us-east-1
```

## Security Notes
- ✅ User has access ONLY to the media bucket
- ✅ Public read access only (no write/delete from web)
- ✅ All uploads go through Django authentication
- ✅ Versioning enabled for backup recovery

## Expected Monthly Costs
- Storage (5GB): ~$0.12/month
- Requests: ~$0.05/month  
- Data Transfer: ~$0.50/month
- **Total: Less than $1/month**

## Folder Structure Created
```
omimi-media-bucket/
├── static/           # UI images (backgrounds, buttons)
├── gallery/
│   ├── swords/      # Sword gallery images
│   └── sales/       # Sales images  
└── blog/
    └── 2024/12/     # Blog images by date
```

## Testing Access
Once created, test the setup:
1. Upload a test image to the bucket
2. Verify it's publicly accessible via URL
3. Confirm IAM user can read/write to bucket

The developer will handle:
- Django configuration
- Image migration script
- Template updates
- Local cleanup