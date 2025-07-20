# 🗡️ Omimi Swords - Railway Deployment Guide

![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![Railway](https://img.shields.io/badge/Railway-131415?style=for-the-badge&logo=railway&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)

A Django-powered website for Omimi Swords, featuring AWS S3 image storage, PostgreSQL database, and optimized for Railway deployment.

## 🚀 Quick Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

## 📋 Table of Contents

- [🌟 Why Railway?](#-why-railway)
- [💰 Cost Comparison](#-cost-comparison)
- [🚀 Deployment Guide](#-deployment-guide)
- [⚙️ Configuration](#️-configuration)
- [🗄️ Database Options](#️-database-options)
- [🔧 Post-Deployment](#-post-deployment)
- [🆘 Troubleshooting](#-troubleshooting)
- [📚 Additional Resources](#-additional-resources)

## 🌟 Why Railway?

Railway is the **optimal choice** for this Django project because:

- ✅ **Auto-detects Django** projects (zero configuration)
- ✅ **$5/month** starting cost (cheaper than alternatives)
- ✅ **Built-in PostgreSQL** option (save on external database costs)
- ✅ **Faster deployments** (3-5 minutes)
- ✅ **Better developer experience** with CLI tools
- ✅ **Automatic HTTPS** and custom domain support

## 💰 Cost Comparison

| Platform | Monthly Cost | Database | Total/Month | Annual Savings |
|----------|-------------|----------|-------------|----------------|
| **Railway (Recommended)** | $5 | Included | **$5** | **-** |
| Railway + Supabase | $5 | $25 | $30 | -$300 |
| Render + Supabase | $7 | $25 | $32 | -$324 |
| AWS Elastic Beanstalk | $15+ | $20+ | $35+ | -$360+ |

**💡 Best Value: Railway with built-in PostgreSQL = $60/year total**

## 🚀 Deployment Guide

### Step 1: Prepare Your Repository

Ensure your code is committed and pushed to GitHub:

```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### Step 2: Create Railway Project

1. **Sign up** at [railway.app](https://railway.app) using your GitHub account
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your `omimi_swords` repository
4. Railway will **automatically detect Django** and start building! 🎉

### Step 3: Configure Environment Variables

In Railway Dashboard → Variables tab, add these **exact** variables:

```bash
# Core Django Settings
DEBUG=False
SECRET_KEY=your-new-production-secret-key-here

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION=us-east-1
AWS_LOCATION=
USE_S3=True

# Email Configuration
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Database (see options below)
DATABASE_URL=your-database-connection-string
```

### Step 4: Choose Database Option

#### Option A: Railway PostgreSQL (Recommended - Save Money!)
1. In Railway Dashboard: **"New"** → **"Database"** → **"PostgreSQL"**
2. Railway auto-generates `DATABASE_URL`
3. **No manual configuration needed!**

#### Option B: Keep External Database (Supabase/etc.)
1. Add your existing `DATABASE_URL` in environment variables
2. Ensure database allows connections from Railway's IP ranges

### Step 5: Deploy & Go Live

**That's it!** Railway automatically:
- ✅ Installs dependencies from `requirements.txt`
- ✅ Runs `collectstatic` for static files
- ✅ Executes database migrations
- ✅ Starts application with Gunicorn
- ✅ Provides live URL (e.g., `https://your-app.up.railway.app`)

**Deployment time: 3-5 minutes** ⚡

## ⚙️ Configuration

### Required Dependencies

```txt
Django>=3.2,<4.0
django-environ
psycopg2-binary
django-ckeditor
django-storages
boto3
dj-database-url
supabase
Pillow
gunicorn
```

### Django Settings Highlights

```python
# settings.py - Key configurations for Railway
ALLOWED_HOSTS = ['*']
USE_S3 = env.bool('USE_S3', default=True)
AWS_QUERYSTRING_AUTH = True  # For private S3 bucket access
DEBUG = env.bool('DEBUG', default=False)

# Railway-specific optimizations
if 'RAILWAY_ENVIRONMENT' in os.environ:
    RAILWAY_STATIC_URL = os.environ.get('RAILWAY_STATIC_URL', '')
    if RAILWAY_STATIC_URL:
        STATIC_URL = RAILWAY_STATIC_URL
```

## 🗄️ Database Options

### Railway PostgreSQL (Recommended)
- **Cost**: Included in $5/month plan
- **Setup**: Automatic via Railway dashboard
- **Backups**: Handled by Railway
- **Connection**: Auto-configured `DATABASE_URL`

### External Database (Supabase, AWS RDS, etc.)
- **Cost**: Additional $25+/month
- **Setup**: Manual `DATABASE_URL` configuration
- **Backups**: Managed by provider
- **Migration**: May require data export/import

### Database Migration (If Switching)

```bash
# Export from existing database
pg_dump "old-database-url" > backup.sql

# Import to Railway PostgreSQL
railway run bash
psql $DATABASE_URL < backup.sql
```

## 🔧 Post-Deployment

### Essential Commands via Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and link project
railway login
railway link

# Create superuser
railway run python manage.py createsuperuser

# View live logs
railway logs

# Open your app
railway open
```

### Production Checklist

- [ ] ✅ Test homepage loads without errors
- [ ] ✅ Admin panel accessible at `/admin/`
- [ ] ✅ S3 images display correctly
- [ ] ✅ Static files (CSS/JS) loading
- [ ] ✅ Database migrations applied
- [ ] ✅ Email functionality working
- [ ] ✅ Custom domain configured (optional)

## 🆘 Troubleshooting

### Common Issues & Solutions

#### Build Failures
```bash
# Check Railway logs
railway logs

# Common fixes:
# 1. Verify all environment variables are set
# 2. Check requirements.txt includes gunicorn
# 3. Ensure no syntax errors in settings.py
```

#### Static Files Not Loading
```bash
# Verify S3 settings
AWS_ACCESS_KEY_ID=correct-key
AWS_SECRET_ACCESS_KEY=correct-secret
AWS_STORAGE_BUCKET_NAME=correct-bucket
```

#### Database Connection Issues
```bash
# For Railway PostgreSQL
railway run python manage.py dbshell

# For external databases
# Verify DATABASE_URL format:
# postgresql://user:password@host:port/database
```

#### Images Not Displaying
```python
# Ensure in settings.py:
AWS_QUERYSTRING_AUTH = True
AWS_QUERYSTRING_EXPIRE = 3600
```

### Getting Help

1. **Railway Documentation**: [docs.railway.app](https://docs.railway.app)
2. **Railway Discord**: Active community support
3. **Django Documentation**: [docs.djangoproject.com](https://docs.djangoproject.com)
4. **AWS S3 Documentation**: [docs.aws.amazon.com/s3/](https://docs.aws.amazon.com/s3/)

## 📚 Additional Resources

### Security Best Practices

```python
# Generate new SECRET_KEY for production
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### Performance Optimization

- Configure proper caching in Django settings
- Use Railway's built-in CDN for static files
- Monitor application performance via Railway metrics
- Set up proper logging for debugging

### Custom Domains

1. Railway Dashboard → Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed
4. Railway provides free SSL certificates automatically

---

## 🏆 Success!

Your Django application should now be live on Railway! 🎉

**Live URL**: `https://your-app-name.up.railway.app`

For support or questions about this deployment, check the troubleshooting section above or reach out to the Railway community.

---

*Built with ❤️ using Django, Railway, AWS S3, and PostgreSQL*