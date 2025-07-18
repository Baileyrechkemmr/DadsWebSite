# 🚀 OMIMI Swords Website - Setup Guide

## Prerequisites
- Python 3.8+
- Git
- AWS Account (for image storage)
- Gmail Account (for contact forms)

## 1. Clone and Setup Project

```bash
git clone https://github.com/Baileyrechkemmr/DadsWebSite.git
cd DadsWebSite

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 2. Environment Variables Setup

### Copy the example file:
```bash
cp .env.example .env
```

### Edit `.env` with your credentials:

#### Django Settings:
```
DEBUG=True
SECRET_KEY=your-unique-secret-key-generate-a-new-one
```

#### AWS S3 Credentials (REQUIRED):
**You need AWS credentials to access the existing image bucket:**

```
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key  
AWS_STORAGE_BUCKET_NAME=ominisword-images
AWS_S3_REGION=us-east-1
```

**⚠️ IMPORTANT:** Contact the project maintainer to get the actual AWS credentials. The bucket name is `ominisword-images` but you'll need the access keys.

#### Email Configuration (for contact forms):
```
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

## 3. Database Setup

```bash
# Apply migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser
```

## 4. Run Development Server

```bash
python manage.py runserver
```

- **Website**: http://localhost:8000
- **Admin**: http://localhost:8000/admin

## 5. Production Deployment

For production:
1. Set `DEBUG=False` in `.env`
2. Change `SECRET_KEY` to a new random value
3. Update `ALLOWED_HOSTS` in settings.py
4. Consider using environment-specific AWS credentials

## 🔐 Security Notes

- **Never commit the `.env` file** (it's in .gitignore)
- The AWS credentials provided access the shared image bucket
- For production, consider creating separate AWS users with minimal permissions
- Email credentials are app-specific passwords, not regular Gmail passwords

## 📸 Image Storage

The website uses AWS S3 for image storage:
- **Bucket**: `ominisword-images`
- **68+ images** already uploaded
- **Signed URLs** for secure access
- **Admin upload** works directly to S3

## 🆘 Troubleshooting

### Images not loading?
- Check AWS credentials in `.env`
- Verify S3 bucket access
- Check Django logs for S3 errors

### Contact forms not working?
- Verify email credentials
- Check Gmail app password setup
- Test SMTP connection

### Database issues?
- Delete `db.sqlite3` and run migrations again
- Check for migration conflicts

---

**Need the actual credentials?** Contact the project maintainer for access to:
- AWS S3 bucket credentials
- Email configuration details
- Production environment setup
