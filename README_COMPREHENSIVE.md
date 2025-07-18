# ⚔️ OMIMI Swords - Complete Website Documentation

## 📖 Table of Contents
- [Project Overview](#-project-overview)
- [Architecture & Tech Stack](#-architecture--tech-stack)
- [Prerequisites & Installation](#-prerequisites--installation)
- [Environment Configuration](#-environment-configuration)
- [S3 Image Storage System](#-s3-image-storage-system)
- [Database Models & Structure](#-database-models--structure)
- [Page-by-Page Breakdown](#-page-by-page-breakdown)
- [Admin Interface Guide](#-admin-interface-guide)
- [Contact Forms & Email System](#-contact-forms--email-system)
- [Development Workflow](#-development-workflow)
- [Troubleshooting](#-troubleshooting)
- [Production Deployment](#-production-deployment)

---

## 🎯 Project Overview

OMIMI Swords is a Django-powered website showcasing artisan sword craftsmanship. The site serves multiple purposes:

- **Portfolio Gallery**: Display custom sword work with professional image storage
- **Class Management**: Sword-making classes with registration and scheduling
- **Sales Platform**: Sell completed swords with detailed descriptions and pricing
- **Blog System**: Share craftsmanship process, tutorials, and updates
- **Travel Resources**: Hotel recommendations for class attendees
- **Contact System**: Multiple contact forms for different inquiries

### Key Features
- 🖼️ **Professional Image Management**: AWS S3 integration with 68+ migrated images
- 🎨 **Rich Content Editing**: CKEditor 5 for blog posts and descriptions
- 📧 **Email Integration**: Automated contact form processing
- 🔐 **Admin Interface**: Comprehensive content management with thumbnails
- 📱 **Responsive Design**: Works across all device types
- 🔒 **Secure Architecture**: Environment-based configuration, signed URLs

---

## 🏗️ Architecture & Tech Stack

### Backend Framework
- **Django 4.2**: Main web framework
- **Python 3.8+**: Programming language
- **SQLite**: Development database (PostgreSQL ready)

### Storage & Media
- **AWS S3**: Cloud storage for all images
- **Signed URLs**: Secure image access with 1-hour expiration
- **django-storages**: S3 integration library

### Content Management
- **CKEditor 5**: Rich text editing for blog posts
- **Django Admin**: Content management interface
- **Image Thumbnails**: Automatic generation in admin

### Communication
- **SMTP (Gmail)**: Email delivery for contact forms
- **Form Processing**: Multiple specialized contact forms

### Dependencies
```
asgiref==3.6.0
boto3==1.38.32
botocore==1.38.32
dj-database-url==2.1.0
Django==4.2
django-ckeditor==6.5.1
django-ckeditor-5==0.2.12
django-environ==0.11.2
django-js-asset==2.0.0
django-phonenumber-field==7.1.0
django-storages==1.14.6
gunicorn==21.2.0
jmespath==1.0.1
packaging==23.2
pillow==11.3.0
python-dateutil==2.9.0.post0
s3transfer==0.13.0
six==1.17.0
sqlparse==0.4.4
typing_extensions==4.8.0
urllib3==2.4.0
```

---

## 🚀 Prerequisites & Installation

### System Requirements
- **Python 3.8+** (tested with 3.9, 3.10, 3.11)
- **Git** for version control
- **Virtual Environment** (venv or virtualenv)
- **AWS Account** (for S3 access)
- **Gmail Account** (for email features)

### Step-by-Step Installation

#### 1. Clone Repository
```bash
git clone https://github.com/Baileyrechkemmr/DadsWebSite.git
cd DadsWebSite
```

#### 2. Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Verify Installation
```bash
python manage.py check
# Should output: System check identified no issues (0 silenced).
```

---

## 🔧 Environment Configuration

### Environment Variables Setup

#### 1. Create Environment File
```bash
cp .env.example .env
```

#### 2. Configure .env File
Edit the `.env` file with the following variables:

```bash
# ===== DJANGO CONFIGURATION =====
DEBUG=True
SECRET_KEY=your-unique-secret-key-here

# ===== AWS S3 CONFIGURATION =====
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=ominisword-images
AWS_S3_REGION=us-east-1

# ===== EMAIL CONFIGURATION =====
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password

# ===== DATABASE CONFIGURATION (Optional) =====
# DATABASE_URL=postgres://user:pass@localhost:5432/dbname
```

### Variable Explanations

#### Django Settings
- **DEBUG**: Set to `True` for development, `False` for production
- **SECRET_KEY**: Django's secret key for security (generate a new one!)

#### AWS S3 Settings
- **AWS_ACCESS_KEY_ID**: Your AWS access key ID
- **AWS_SECRET_ACCESS_KEY**: Your AWS secret access key
- **AWS_STORAGE_BUCKET_NAME**: S3 bucket name (`ominisword-images`)
- **AWS_S3_REGION**: AWS region (`us-east-1`)

#### Email Settings
- **EMAIL_HOST_USER**: Gmail address for sending emails
- **EMAIL_HOST_PASSWORD**: Gmail app password (not regular password!)

### Generate Secret Key
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### Gmail App Password Setup
1. Enable 2-factor authentication on Gmail
2. Go to Google Account settings
3. Security → App passwords
4. Generate password for "Mail"
5. Use this password in EMAIL_HOST_PASSWORD

---

## ☁️ S3 Image Storage System

### S3 Architecture Overview

The website uses AWS S3 for all image storage with the following structure:

```
ominisword-images/
├── static/ui/                 # Website UI elements
│   ├── dadsBanerOne.jpeg
│   ├── classes_image_1.png
│   └── blog.png
├── gallery/swords/            # Sword showcase images
│   ├── sword_one.webp
│   ├── 14.jpg
│   └── cef.jpg
└── blog/2024/12/             # Blog post images
    ├── 100_3589.png
    ├── PXL_20230207_214659597_1.jpg
    └── Graphic-Design-Course-in-Bangalore.jpg
```

### S3 Configuration in Django

#### settings.py Configuration
```python
# AWS S3 Settings
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = env('AWS_S3_REGION', default='us-east-1')
AWS_DEFAULT_ACL = None  # Modern S3 buckets don't use ACLs
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

# S3 Media Settings - Using signed URLs for private bucket
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_QUERYSTRING_AUTH = True  # Use signed URLs
AWS_QUERYSTRING_EXPIRE = 3600  # URLs expire after 1 hour
```

### S3 Integration Benefits
- **Scalable Storage**: No server disk space limitations
- **CDN Performance**: Fast global image delivery
- **Automatic Backups**: AWS handles redundancy
- **Security**: Signed URLs prevent unauthorized access
- **Cost Effective**: Pay only for storage used (~$10-20/year)

### Image Upload Process
1. User uploads image through Django admin
2. Django processes the image
3. Image automatically uploaded to S3
4. S3 URL stored in database
5. Signed URLs generated for secure access

---

## 🗄️ Database Models & Structure

### Model Overview

#### Year Model
```python
class Year(models.Model):
    title = models.CharField(default="year", max_length=4)
    class_year = models.IntegerField()
```
**Purpose**: Organize classes by year

#### Classes Model
```python
class Classes(models.Model):
    class_title = models.CharField(max_length=250)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(default="null")
    class_slots = models.IntegerField(default=0)
```
**Purpose**: Manage sword-making class information

#### Sword_img Model
```python
class Sword_img(models.Model):
    item_number = models.IntegerField(default=0)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    description = models.TextField(default="null")
```
**Purpose**: Gallery showcase swords

#### Sword_sales Model
```python
class Sword_sales(models.Model):
    item_number = models.IntegerField(default=0)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    description = models.TextField(default="null")
    price = models.CharField(max_length=50)
```
**Purpose**: Swords available for purchase

#### Hotel Model
```python
class Hotel(models.Model):
    city_name = models.CharField(max_length=100)
    hotel_name = models.CharField(max_length=250)
    address = models.CharField(max_length=100)
    description = models.TextField(default="null")
    distance = models.CharField(max_length=100)
    phone = models.CharField(max_length=100, default="515-555-5555")
```
**Purpose**: Hotel recommendations for class attendees

#### Blog System
```python
class BlogImages(models.Model):
    image = models.ImageField(upload_to='static/', blank=True, null=True)

class Blog(models.Model):
    date = models.DateField(auto_now_add=True)
    description = RichTextField(default="null")
    images = models.ManyToManyField(BlogImages, blank=True)
```
**Purpose**: Blog posts with rich text and multiple images

### Database Relationships
- **Blog ↔ BlogImages**: Many-to-Many (one blog post can have multiple images)
- **Classes ↔ Year**: Foreign Key relationship (if implemented)
- All other models are independent

### Migration Commands
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# View migration status
python manage.py showmigrations
```

---

## 📄 Page-by-Page Breakdown

### 1. Home Page (`/`)
**Template**: `projects/templates/projects/home.html`
**View**: `home(request)` in `views.py`
**Purpose**: Landing page showcasing featured swords

**Functionality**:
- Displays sword gallery preview
- Navigation to all other sections
- Hero image and welcome message

**Data Source**: `Sword_img.objects`

### 2. About Page (`/about/`)
**Template**: `projects/templates/projects/about.html`
**View**: `about(request)` in `views.py`
**Purpose**: Information about the craftsman and process

**Functionality**:
- Static content about the artisan
- Craftsmanship philosophy
- Contact information

### 3. Gallery Page (`/gallery/`)
**Template**: `projects/templates/projects/gallery.html`
**View**: `gallery(request)` in `views.py`
**Purpose**: Complete sword portfolio showcase

**Functionality**:
- Displays all `Sword_img` objects
- Image grid layout
- Links to detail pages
- S3 image integration

**Data Source**: `Sword_img.objects.all()`

### 4. Sword Detail Page (`/gallery/<int:sword_img_id>/`)
**Template**: `projects/templates/projects/details_s.html`
**View**: `details_s(request, sword_img_id)` in `views.py`
**Purpose**: Individual sword details

**Functionality**:
- Large image display
- Detailed description
- Technical specifications
- Link to order form

**Data Source**: `get_object_or_404(Sword_img, pk=sword_img_id)`

### 5. Classes Page (`/classes/`)
**Template**: `projects/templates/projects/classes.html`
**View**: `classes(request)` in `views.py`
**Purpose**: Class information and registration

**Functionality**:
- Display available classes
- Registration form processing
- Hotel recommendations
- Email notification system

**Data Sources**: 
- `Classes.objects.all()`
- `Hotel.objects.all()`
- `Year.objects.all()`

**Form Processing**:
```python
if request.method == 'POST':
    # Extract form data
    class_name = request.POST.get('class_name', '')
    email = request.POST.get('email', '')
    # ... more fields
    
    # Send email notification
    send_mail(
        'class sign up form',
        messages,
        'settings.EMAIL_HOST_USER',
        ['bigearincornpatch@gmail.com'],
        fail_silently=False
    )
```

### 6. Sales Page (`/sales/`)
**Template**: `projects/templates/projects/sales.html`
**View**: `sales(request)` in `views.py`
**Purpose**: Swords available for purchase

**Functionality**:
- Display available swords with prices
- Purchase inquiry form
- Email processing for orders

**Data Source**: `Sword_sales.objects.all()`

### 7. Sales Detail Page (`/sales/<int:sword_sales_id>/`)
**Template**: `projects/templates/projects/details_sales.html`
**View**: `details_sales(request, sword_sales_id)` in `views.py`
**Purpose**: Individual sword sale details

**Functionality**:
- Large image display
- Price and description
- Purchase form

### 8. Blog Page (`/blog/`)
**Template**: `projects/templates/projects/blog.html`
**View**: `blog(request)` in `views.py`
**Purpose**: Blog posts and updates

**Functionality**:
- Display all blog posts
- Rich text content
- Multiple images per post
- Date-based organization

**Data Source**: `Blog.objects.all()`

### 9. Order Form Page (`/order/`)
**Template**: `projects/templates/projects/order_form.html`
**View**: `order_form(request)` in `views.py`
**Purpose**: Custom sword order requests

**Functionality**:
- Detailed order form
- Custom specifications
- Email processing

### 10. Hotel Detail Page (`/hotel/<int:hotel_id>/`)
**Template**: `projects/templates/projects/details_h.html`
**View**: `details_h(request, hotel_id)` in `views.py`
**Purpose**: Hotel recommendation details

### 11. Movie Page (`/movie/`)
**Template**: `projects/templates/projects/movie.html`
**View**: `movie(request)` in `views.py`
**Purpose**: Video content showcase

---

## 🔐 Admin Interface Guide

### Access the Admin Panel
```
URL: http://localhost:8000/admin/
Default credentials: Create with `python manage.py createsuperuser`
```

### Admin Models Overview

#### 1. Sword_img Admin
**Features**:
- Image thumbnails (50x50px with rounded corners)
- Search by item number and description
- Filter by item number
- Preview images before saving

**Admin Code**:
```python
@admin.register(Sword_img)
class Sword_imgAdmin(admin.ModelAdmin):
    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return "No Image"
    thumbnail.short_description = 'Preview'
    
    list_display = ['item_number', 'thumbnail', 'description']
    search_fields = ['item_number', 'description']
    list_filter = ['item_number']
    readonly_fields = ['thumbnail']
```

#### 2. Sword_sales Admin
**Features**:
- Image thumbnails with pricing
- Search by item number, description, and price
- Enhanced filtering options

#### 3. Blog Admin
**Features**:
- Rich text editing with CKEditor 5
- Multiple image attachments
- Date-based organization
- Inline image management

#### 4. BlogImages Admin
**Features**:
- Large image thumbnails (80x60px)
- Direct S3 upload
- Image preview

#### 5. Classes Admin
**Features**:
- Date range management
- Class capacity tracking
- Search and filter capabilities

#### 6. Hotel Admin
**Features**:
- Location-based organization
- Contact information management
- Distance and address tracking

### Using the Admin Interface

#### Adding New Content
1. **Log into admin panel**
2. **Select model type** (Sword_img, Blog, etc.)
3. **Click "Add [Model Name]"**
4. **Fill in required fields**
5. **Upload images** (automatically goes to S3)
6. **Save and continue** or **Save and add another**

#### Managing Images
- **Upload**: Images automatically upload to S3
- **Preview**: Thumbnails show in list view
- **Edit**: Click thumbnail to view full size
- **Delete**: Removes from both database and S3

#### Rich Text Editing (Blog Posts)
- **CKEditor 5** with full formatting options
- **Image insertion** directly in text
- **Link management**
- **Table support**
- **Code highlighting**

#### Bulk Operations
- **Select multiple items** with checkboxes
- **Apply bulk actions** from dropdown
- **Export data** (if configured)

---

## 📧 Contact Forms & Email System

### Email Configuration

#### SMTP Settings in settings.py
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST_USER = 'brechkemmer01@gmail.com'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_PASSWORD = 'bqtlyuyacnxwbjyj'  # App password
```

### Contact Forms Available

#### 1. Class Registration Form
**Location**: `/classes/` page
**Purpose**: Register for sword-making classes

**Fields**:
- Class name selection
- Personal information (name, email)
- Complete address
- Phone number

**Email Template**:
```python
messages = f"""
Class Name: {class_name}
Email: {email}
Name: {name}
Address 1: {address_1}
Address 2: {address_2}
City: {city}
State or Province: {state_or_province}
Zip Code: {zip_code}
Country: {country}
Phone Number: {phone_number}
"""
```

#### 2. Custom Order Form
**Location**: `/order/` page
**Purpose**: Request custom sword creation

**Fields**:
- Personal information
- Address details
- Sword specifications:
  - Depth of sori (curvature)
  - Length of blade
  - Type of steel
  - Other specifications

#### 3. Sales Inquiry Form
**Location**: `/sales/` page
**Purpose**: Purchase existing swords

**Fields**:
- Selected item number
- Customer information
- Shipping address

### Email Processing Flow
1. **User submits form**
2. **Django processes POST data**
3. **Form validation** (basic)
4. **Email composition** with form data
5. **SMTP delivery** via Gmail
6. **Confirmation** (implicit - no error = success)

### Email Recipients
All forms currently send to: `bigearincornpatch@gmail.com`

### Error Handling
- `fail_silently=False` ensures email errors are visible
- Form submissions without email configuration will raise exceptions
- SMTP errors are logged to Django console

---

## 🛠️ Development Workflow

### Daily Development Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Check for new changes
git pull origin main

# Install any new dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Run development server
python manage.py runserver
```

### Making Changes

#### 1. Model Changes
```bash
# After modifying models.py
python manage.py makemigrations
python manage.py migrate
```

#### 2. Static Files
```bash
# Collect static files for production
python manage.py collectstatic
```

#### 3. Testing Changes
```bash
# Check for issues
python manage.py check

# Run tests (if available)
python manage.py test
```

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature-name

# Make your changes
# ... edit files ...

# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: Add new feature description"

# Push to remote
git push origin feature/new-feature-name

# Create pull request on GitHub
```

### Code Quality Standards
- **PEP 8**: Python code formatting
- **Descriptive commits**: Clear commit messages
- **Environment separation**: Never commit credentials
- **Documentation**: Update README for major changes

---

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. Images Not Loading
**Problem**: Images not displaying on website
**Symptoms**: Broken image icons, 404 errors

**Solutions**:
```bash
# Check S3 credentials
python -c "
import boto3, os
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'omimi.settings')
import django; django.setup()
s3 = boto3.client('s3', 
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
print('S3 connection successful:', s3.list_buckets())
"

# Test S3 integration
python test_s3_integration.py

# Check specific files
python check_s3_files.py
```

#### 2. Email Forms Not Working
**Problem**: Contact forms not sending emails
**Symptoms**: Form submission without email delivery

**Solutions**:
```python
# Test email settings
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@email.com', ['to@email.com'])
```

**Check**:
- Gmail app password is correct
- 2-factor authentication enabled
- SMTP settings match Gmail requirements

#### 3. Admin Panel Issues
**Problem**: Can't access admin or thumbnails not showing

**Solutions**:
```bash
# Create superuser
python manage.py createsuperuser

# Check admin registration
python manage.py shell
>>> from django.contrib import admin
>>> print(admin.site._registry.keys())
```

#### 4. Migration Errors
**Problem**: Database migration failures

**Solutions**:
```bash
# Reset migrations (CAREFUL - loses data)
rm -rf projects/migrations/00*.py
python manage.py makemigrations projects
python manage.py migrate

# Or rollback specific migration
python manage.py migrate projects 0027
```

#### 5. Environment Variable Issues
**Problem**: Settings not loading from .env

**Solutions**:
```bash
# Check .env file exists
ls -la .env

# Verify environment loading
python manage.py shell
>>> import os
>>> print(os.environ.get('AWS_ACCESS_KEY_ID'))
```

#### 6. S3 Permission Errors
**Problem**: S3 access denied errors

**Solutions**:
- Verify AWS credentials are correct
- Check S3 bucket permissions
- Confirm bucket region matches settings
- Test with AWS CLI: `aws s3 ls s3://ominisword-images`

### Debug Mode
Enable detailed error information:
```python
# In .env file
DEBUG=True

# View detailed error pages
# Check Django console output
```

### Log Analysis
```bash
# Django development server logs
# Check console output for errors

# Enable Django logging in settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

---

## 🚀 Production Deployment

### Pre-Deployment Checklist
- [ ] `DEBUG=False` in production environment
- [ ] New `SECRET_KEY` generated for production
- [ ] `ALLOWED_HOSTS` configured
- [ ] Database configured (PostgreSQL recommended)
- [ ] Static files served properly
- [ ] S3 credentials secured
- [ ] Email credentials configured
- [ ] HTTPS enabled
- [ ] Domain configured

### Environment Variables for Production
```bash
# Production .env
DEBUG=False
SECRET_KEY=new-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL example)
DATABASE_URL=postgres://user:password@host:5432/dbname

# AWS S3 (consider separate production bucket)
AWS_ACCESS_KEY_ID=production-access-key
AWS_SECRET_ACCESS_KEY=production-secret-key
AWS_STORAGE_BUCKET_NAME=production-bucket-name

# Email (production email account)
EMAIL_HOST_USER=production@yourdomain.com
EMAIL_HOST_PASSWORD=production-app-password
```

### Deployment Platforms

#### Heroku Deployment
```bash
# Install Heroku CLI
# Create Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set AWS_ACCESS_KEY_ID=your-key
# ... set all other variables

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser
```

#### DigitalOcean/AWS EC2
```bash
# Server setup
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx

# Clone repository
git clone https://github.com/Baileyrechkemmr/DadsWebSite.git
cd DadsWebSite

# Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Configure environment variables
cp .env.example .env
# Edit .env with production values

# Run migrations
python manage.py migrate
python manage.py collectstatic

# Start with Gunicorn
gunicorn omimi.wsgi:application --bind 0.0.0.0:8000
```

### Static Files in Production
```python
# settings.py additions for production
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Option 1: Serve static files from S3
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Option 2: Serve static files from server
# Configure nginx to serve /static/ directory
```

### Database Migration for Production
```bash
# Backup existing data
python manage.py dumpdata > backup.json

# Apply migrations
python manage.py migrate

# Load data if needed
python manage.py loaddata backup.json
```

### SSL Certificate
```bash
# Using Let's Encrypt with certbot
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### Monitoring and Maintenance
- Set up error logging (Sentry, Django logging)
- Configure database backups
- Monitor S3 usage and costs
- Set up uptime monitoring
- Regular security updates

---

## 📞 Support and Contact

### Getting Help
1. **Check this documentation** first
2. **Search existing GitHub issues**
3. **Create new issue** with detailed description
4. **Contact maintainer** for credentials

### Contributing
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Update documentation
5. Submit pull request

### Reporting Issues
Include in your issue report:
- Python version
- Django version
- Error messages (full stack trace)
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable

---

**Last Updated**: January 2025  
**Version**: 2.0  
**Status**: ✅ Production Ready

This documentation covers the complete OMIMI Swords website system. For additional questions or credential access, contact the project maintainer.