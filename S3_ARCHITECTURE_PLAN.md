# S3 Architecture Plan for Omimi Swords on Render

## Bucket Strategy for 1,000 Images/Year

### Option A: Multiple Buckets (Your Preference)
```
🪣 omimi-static-assets
├── css/
├── js/
├── images/
│   ├── backgrounds/
│   ├── logos/
│   └── ui-elements/

🪣 omimi-blog-images  
├── 2024/
│   ├── 01/
│   ├── 02/
│   └── ...
└── 2025/

🪣 omimi-gallery-images
├── swords/
│   ├── katana/
│   ├── wakizashi/
│   └── tanto/
├── sales/
└── process-photos/
```

### Option B: Single Bucket with Prefixes (Alternative)
```
🪣 omimi-media
├── static/
├── blog/
└── gallery/
```

## Cost Analysis for Your Scale

### Annual Costs (1,000 images/year @ 3MB average):
```
Storage (3GB): $0.69/year
Requests (uploads): $0.50/year  
CloudFront (100GB transfer): $8.50/year
Total: ~$10/year per bucket

3 buckets = ~$30/year total
Single bucket = ~$10/year

Recommendation: Single bucket with prefixes saves $20/year
```

## Django Configuration for Multi-Bucket Setup

### Custom Storage Classes
```python
# omimi/storage_backends.py
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class StaticStorage(S3Boto3Storage):
    bucket_name = settings.AWS_STATIC_BUCKET_NAME
    custom_domain = f'{bucket_name}.s3.amazonaws.com'
    default_acl = 'public-read'

class BlogImageStorage(S3Boto3Storage):
    bucket_name = settings.AWS_BLOG_BUCKET_NAME
    custom_domain = f'{bucket_name}.s3.amazonaws.com'
    default_acl = 'public-read'
    file_overwrite = False

class GalleryImageStorage(S3Boto3Storage):
    bucket_name = settings.AWS_GALLERY_BUCKET_NAME
    custom_domain = f'{bucket_name}.s3.amazonaws.com'
    default_acl = 'public-read'
    file_overwrite = False
```

### Settings Configuration
```python
# omimi/settings.py
import os
from pathlib import Path

# Render Environment Detection
if os.environ.get('RENDER'):
    # Production on Render
    DEBUG = False
    
    # Multi-bucket S3 setup
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION', 'us-east-1')
    
    # Bucket names
    AWS_STATIC_BUCKET_NAME = 'omimi-static-assets'
    AWS_BLOG_BUCKET_NAME = 'omimi-blog-images'  
    AWS_GALLERY_BUCKET_NAME = 'omimi-gallery-images'
    
    # Static files
    STATICFILES_STORAGE = 'omimi.storage_backends.StaticStorage'
    STATIC_URL = f'https://{AWS_STATIC_BUCKET_NAME}.s3.amazonaws.com/'
    
    # Default media storage (for blog images)
    DEFAULT_FILE_STORAGE = 'omimi.storage_backends.BlogImageStorage'
    MEDIA_URL = f'https://{AWS_BLOG_BUCKET_NAME}.s3.amazonaws.com/'
    
else:
    # Local development
    DEBUG = True
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
```

### Updated Models with Custom Storage
```python
# projects/models.py
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.html import strip_tags
from ckeditor.fields import RichTextField
from omimi.storage_backends import GalleryImageStorage, BlogImageStorage
from PIL import Image as PILImage
import os

def get_sword_upload_path(instance, filename):
    """Generate organized upload path for sword images"""
    return f'swords/{instance.item_number}/{filename}'

def get_sales_upload_path(instance, filename):
    """Generate organized upload path for sales images"""  
    return f'sales/{instance.item_number}/{filename}'

def get_blog_upload_path(instance, filename):
    """Generate organized upload path for blog images"""
    from datetime import datetime
    now = datetime.now()
    return f'{now.year}/{now.month:02d}/{filename}'

class Sword_img(models.Model):
    item_number = models.IntegerField(default=0, unique=True)
    image = models.ImageField(
        upload_to=get_sword_upload_path,
        storage=GalleryImageStorage(),
        blank=True, 
        null=True
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Auto-resize large images
        if self.image and hasattr(self.image, 'path'):
            img_path = self.image.path
            with PILImage.open(img_path) as img:
                if img.height > 1200 or img.width > 1200:
                    output_size = (1200, 1200)
                    img.thumbnail(output_size, PILImage.LANCZOS)
                    img.save(img_path, quality=85, optimize=True)

    def __str__(self):
        return f"Sword {self.item_number}"

    class Meta:
        ordering = ['item_number']

class Sword_sales(models.Model):
    item_number = models.IntegerField(default=0, unique=True)
    image = models.ImageField(
        upload_to=get_sales_upload_path,
        storage=GalleryImageStorage(),
        blank=True, 
        null=True
    )
    description = models.TextField(blank=True)
    price = models.CharField(max_length=50)
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale Item {self.item_number}"

class BlogImages(models.Model):
    image = models.ImageField(
        upload_to=get_blog_upload_path,
        storage=BlogImageStorage(),
        blank=True, 
        null=True
    )
    alt_text = models.CharField(max_length=200, blank=True, help_text="Alternative text for accessibility")
    caption = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Blog Image {self.id} - {self.created_at.strftime('%Y-%m-%d')}"

    class Meta:
        ordering = ['-created_at']

class Blog(models.Model):
    title = models.CharField(max_length=200, blank=True)
    date = models.DateField(auto_now_add=True)
    description = RichTextField(blank=True)
    images = models.ManyToManyField(BlogImages, blank=True)
    featured_image = models.ImageField(
        upload_to=get_blog_upload_path,
        storage=BlogImageStorage(),
        blank=True, 
        null=True,
        help_text="Main image for this blog post"
    )
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def stripped_rich_field(self):
        return strip_tags(self.description)
    
    def __str__(self):
        return self.title or f"Blog Post {self.date}"

    class Meta:
        ordering = ['-date']
```

## Admin Upload Experience

### Enhanced Admin Interface
```python
# projects/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db import models
from django.forms import Textarea
from .models import Sword_img, Sword_sales, BlogImages, Blog

@admin.register(Sword_img)
class Sword_imgAdmin(admin.ModelAdmin):
    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="80" height="80" style="object-fit: cover; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return format_html('<div style="width: 80px; height: 80px; background: #f0f0f0; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #666;">No Image</div>')
    thumbnail.short_description = 'Preview'

    def image_info(self, obj):
        if obj.image:
            try:
                return format_html(
                    '<div style="font-size: 12px;">'
                    '<strong>Size:</strong> {}x{}<br>'
                    '<strong>File:</strong> {:.1f} KB<br>'
                    '<strong>S3 Path:</strong> {}'
                    '</div>',
                    obj.image.width,
                    obj.image.height,
                    obj.image.size / 1024,
                    obj.image.name
                )
            except:
                return "Image info unavailable"
        return "No image"
    image_info.short_description = 'Image Details'

    def s3_url(self, obj):
        if obj.image:
            return format_html(
                '<a href="{}" target="_blank" style="color: #0066cc;">View Full Size →</a>',
                obj.image.url
            )
        return "No image"
    s3_url.short_description = 'S3 Link'

    list_display = ['item_number', 'thumbnail', 'description_preview', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['item_number', 'description']
    readonly_fields = ['thumbnail', 'image_info', 's3_url', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Sword Information', {
            'fields': ('item_number', 'description'),
            'classes': ('wide',)
        }),
        ('Image Upload', {
            'fields': ('image', 'thumbnail', 'image_info', 's3_url'),
            'classes': ('wide',),
            'description': 'Images are automatically uploaded to S3 and optimized.'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def description_preview(self, obj):
        return obj.description[:50] + "..." if len(obj.description) > 50 else obj.description
    description_preview.short_description = 'Description'

    # Custom form widget for better textarea
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 60})},
    }

@admin.register(BlogImages)
class BlogImagesAdmin(admin.ModelAdmin):
    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 8px;" />',
                obj.image.url
            )
        return "No image"
    thumbnail.short_description = 'Preview'

    def image_path(self, obj):
        if obj.image:
            return obj.image.name
        return "No image"
    image_path.short_description = 'S3 Path'

    list_display = ['id', 'thumbnail', 'alt_text', 'image_path', 'created_at']
    list_filter = ['created_at']
    search_fields = ['alt_text', 'caption']
    fields = ['image', 'alt_text', 'caption', 'thumbnail']
    readonly_fields = ['thumbnail']

    # Inline editing capability
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

class BlogImagesInline(admin.TabularInline):
    model = Blog.images.through
    extra = 1
    verbose_name = "Additional Image"
    verbose_name_plural = "Additional Images"

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    def featured_thumbnail(self, obj):
        if obj.featured_image:
            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 4px;" />',
                obj.featured_image.url
            )
        return "No featured image"
    featured_thumbnail.short_description = 'Featured'

    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = 'Additional Images'

    list_display = ['title', 'featured_thumbnail', 'date', 'image_count', 'is_published']
    list_filter = ['date', 'is_published', 'created_at']
    search_fields = ['title', 'description']
    inlines = [BlogImagesInline]
    
    fieldsets = (
        ('Blog Content', {
            'fields': ('title', 'description', 'is_published')
        }),
        ('Featured Image', {
            'fields': ('featured_image', 'featured_thumbnail'),
            'description': 'Main image for this blog post'
        }),
        ('Metadata', {
            'fields': ('date', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['featured_thumbnail', 'date', 'created_at']

# Custom CSS for better admin experience
# static/admin/css/custom_admin.css
"""
.field-thumbnail img {
    border: 2px solid #ddd;
    transition: transform 0.2s;
}

.field-thumbnail img:hover {
    transform: scale(1.1);
    border-color: #0066cc;
}

.fieldset {
    margin: 20px 0;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
}
"""
```

## Render Environment Setup

### Environment Variables for Render
```bash
# In Render Dashboard > Environment Variables
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_S3_REGION=us-east-1
DJANGO_ENV=production
```

### Render Build Script
```bash
# build.sh
#!/usr/bin/env bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
```

## File Organization in S3

### Gallery Bucket Structure
```
omimi-gallery-images/
├── swords/
│   ├── 001/
│   │   ├── katana_001_main.jpg
│   │   ├── katana_001_detail.jpg
│   │   └── katana_001_process.jpg
│   └── 002/
└── sales/
    ├── 101/
    └── 102/
```

### Blog Bucket Structure  
```
omimi-blog-images/
├── 2024/
│   ├── 01/
│   │   ├── forge_fire_process.jpg
│   │   └── new_technique_demo.jpg
│   └── 02/
└── 2025/
```

This gives you:
- ✅ Organized, scalable structure
- ✅ Easy backup/management per category
- ✅ Different access policies per bucket if needed
- ✅ Clear cost tracking per image type
- ✅ Professional admin upload experience
- ✅ Automatic image optimization
- ✅ Global CDN delivery via S3