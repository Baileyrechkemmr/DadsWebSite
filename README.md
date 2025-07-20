# Omimi Swords - Railway Deployment

Django website for Omimi Swords with AWS S3 image storage.

## Quick Railway Deploy

1. **Connect to Railway**
   - Go to [railway.app](https://railway.app)
   - Deploy from GitHub repo
   - Select this branch

2. **Add Database**
   - Add PostgreSQL service in Railway
   - Railway auto-connects to your app

3. **Environment Variables**
   ```
   DEBUG=False
   SECRET_KEY=your-production-secret-key
   AWS_ACCESS_KEY_ID=your-aws-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret
   AWS_STORAGE_BUCKET_NAME=your-bucket
   AWS_S3_REGION=us-east-1
   USE_S3=True
   EMAIL_HOST_USER=your-email
   EMAIL_HOST_PASSWORD=your-password
   ```

4. **Create Admin User**
   ```bash
   railway run python manage.py createsuperuser
   ```

Cost: ~$5/month total with Railway PostgreSQL included.