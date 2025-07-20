# AWS Blog Backend Setup Guide

This guide will help you set up the AWS-powered blog backend for the Omimi Swords website.

## 🎯 What You Get

✅ **DynamoDB** for blog post storage (serverless, scalable)  
✅ **S3** for image storage (already configured)  
✅ **Django Admin** interface (familiar editing experience)  
✅ **Rich text editor** with image support  
✅ **Search functionality** across blog posts  
✅ **Tag-based organization**  
✅ **View counting** and analytics  
✅ **Caching** for improved performance  

## 📋 Prerequisites

1. AWS Account with appropriate permissions
2. Python packages: `boto3`, `django-environ`
3. Existing S3 bucket for images (you already have this)

## 🚀 Setup Steps

### 1. Install Required Packages

```bash
pip install boto3 django-environ
```

### 2. AWS Permissions Setup

Your AWS user needs these permissions:

**DynamoDB Permissions:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:CreateTable",
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Scan",
                "dynamodb:Query",
                "dynamodb:DescribeTable"
            ],
            "Resource": "arn:aws:dynamodb:*:*:table/omimi-blog-posts*"
        }
    ]
}
```

**S3 Permissions** (you likely already have these):
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
                "arn:aws:s3:::your-bucket-name",
                "arn:aws:s3:::your-bucket-name/*"
            ]
        }
    ]
}
```

### 3. Environment Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Fill in your AWS credentials in `.env`:
   ```bash
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_STORAGE_BUCKET_NAME=your_existing_bucket_name
   AWS_S3_REGION=us-east-1
   DYNAMODB_BLOG_TABLE=omimi-blog-posts
   ```

### 4. Database Migration (Optional)

If you want to migrate existing blog posts from SQLite to DynamoDB:

```python
# Run this in Django shell: python manage.py shell
from projects.models import Blog
from projects.aws_blog_service import blog_service

# Migrate existing blog posts
for old_blog in Blog.objects.all():
    blog_service.create_blog_post(
        title=f"Post from {old_blog.date}",
        content=old_blog.description,
        images=[img.image.url for img in old_blog.images.all()],
        tags=[]
    )
    print(f"Migrated blog post from {old_blog.date}")
```

### 5. Test the Setup

1. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

2. **Access Django Admin:**
   - Go to `http://localhost:8000/admin`
   - Look for "AWS Blog Posts" section
   - Try creating a new blog post

3. **View the blog:**
   - Go to `http://localhost:8000/aws-blog/`
   - Your posts should appear here

### 6. Update Navigation Links

Update your existing templates to point to the new blog:
- Change `{% url 'blog' %}` to `{% url 'aws_blog' %}`
- Or keep both and let users choose

## 🔧 Key Features

### Django Admin Interface
- Create/edit blog posts with rich text editor
- Upload images directly to S3
- Tag management
- Publish/unpublish posts
- View count tracking

### Frontend Features
- Responsive design matching your existing site
- Search functionality
- Tag-based filtering
- Pagination
- Image optimization
- Social sharing buttons

### AWS Integration
- **DynamoDB**: Serverless blog post storage
- **S3**: Image hosting with signed URLs
- **Auto-scaling**: Handles traffic spikes automatically
- **Cost-effective**: Pay only for what you use

## 📊 Monitoring & Analytics

### View Counts
Each blog post automatically tracks view counts, stored in DynamoDB.

### AWS CloudWatch
Monitor your DynamoDB usage:
- Read/Write capacity units
- Request latency
- Error rates

### Django Logging
Logs are written to `logs/aws_blog.log` for debugging.

## 🛠 Troubleshooting

### Common Issues

1. **DynamoDB Access Denied**
   - Check your AWS credentials
   - Verify IAM permissions
   - Ensure region is correct

2. **Images Not Loading**
   - Check S3 bucket permissions
   - Verify `AWS_QUERYSTRING_AUTH = True` in settings
   - Check signed URL expiration time

3. **Blog Posts Not Appearing**
   - Check if posts are marked as "published"
   - Look at Django logs for errors
   - Verify DynamoDB table exists

### Debug Commands

```python
# Django shell debugging
from projects.aws_blog_service import blog_service

# Test DynamoDB connection
print(blog_service.table.table_status)

# List all blog posts
for post in blog_service.get_all_blog_posts():
    print(f"{post['title']} - {post['created_date']}")
```

## 🚀 Going to Production

### Performance Optimizations
1. Enable DynamoDB on-demand billing
2. Set up CloudFront for S3 images
3. Use Redis for Django caching
4. Enable Django's static file compression

### Security
1. Use IAM roles instead of access keys in production
2. Enable S3 bucket versioning
3. Set up DynamoDB point-in-time recovery
4. Use HTTPS everywhere

## 💰 Cost Estimation

**DynamoDB**: ~$0.25/month for 1M reads, 1M writes  
**S3**: ~$0.50/month for 10GB storage + requests  
**Total**: Less than $1/month for typical blog usage

## 🎉 Next Steps

1. **Test everything** with a few blog posts
2. **Migrate existing content** if needed
3. **Update your templates** to use the new blog URLs
4. **Monitor AWS costs** and usage
5. **Consider adding features** like:
   - Email subscriptions
   - Comments system
   - RSS feed
   - Full-text search with OpenSearch

---

**Need Help?** Check the logs in `logs/aws_blog.log` or use Django's debug mode to troubleshoot issues.