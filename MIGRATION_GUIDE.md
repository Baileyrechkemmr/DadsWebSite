# Image Setup Migration Guide for Omimi Swords

## Current Setup Analysis

Your project uses an **unconventional but functional** image handling approach:

### What You Currently Have:
```python
# models.py - Using CharField instead of ImageField
class Sword_img(models.Model):
    image = models.CharField(default="null", max_length=100)
    # image = models.ImageField(upload_to='media/')  # COMMENTED OUT

# templates - Manual URL construction
<img src="{{ MEDIA_URL }}{{ sword_img.image }}" class="card-img-top">

# admin.py - Commented out thumbnail functionality
# def thumbnail(self, object):
#     return format_html('<img src="{}" width="40" />'.format(object.image.url))
```

### Issues with Current Approach:
- ❌ Manual file management required
- ❌ No upload validation
- ❌ No automatic URL generation
- ❌ Multiple image directories (`media/`, `images/`)
- ❌ Risk of broken links if files moved
- ❌ No image metadata (width, height, file size)

## Migration Options

### Option 1: Quick Fix (Minimal Changes)
**Best for:** Getting benefits with minimal code changes

### Option 2: Full Migration (Recommended)
**Best for:** Long-term maintainability and Django best practices

---

## Option 1: Quick Fix Migration

### Step 1: Add New ImageField Alongside CharField
```python
# projects/models.py
class Sword_img(models.Model):
    item_number = models.IntegerField(default=0)
    # Keep old field for now
    image = models.CharField(default="null", max_length=100)
    # Add new field
    image_file = models.ImageField(upload_to='images/swords/', blank=True, null=True)
    description = models.TextField(default="null")

    def get_image_url(self):
        """Get image URL from either field"""
        if self.image_file:
            return self.image_file.url
        elif self.image and self.image != "null":
            return f"/media/{self.image}"
        return "/static/images/placeholder.jpg"  # fallback image

class Sword_sales(models.Model):
    item_number = models.IntegerField(default=0)
    image = models.CharField(default="null", max_length=100)
    image_file = models.ImageField(upload_to='images/sales/', blank=True, null=True)
    description = models.TextField(default="null")
    price = models.CharField(max_length=50)

    def get_image_url(self):
        if self.image_file:
            return self.image_file.url
        elif self.image and self.image != "null":
            return f"/media/{self.image}"
        return "/static/images/placeholder.jpg"

class BlogImages(models.Model):
    image = models.CharField(default="null", max_length=100)
    image_file = models.ImageField(upload_to='images/blog/', blank=True, null=True)

    def get_image_url(self):
        if self.image_file:
            return self.image_file.url
        elif self.image and self.image != "null":
            return f"/media/{self.image}"
        return "/static/images/placeholder.jpg"
```

### Step 2: Create Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Update Templates
```html
<!-- projects/templates/projects/gallery.html -->
<!-- Change from: -->
<img src="{{ MEDIA_URL }}{{ sword_img.image }}" class="card-img-top">

<!-- To: -->
<img src="{{ sword_img.get_image_url }}" class="card-img-top" alt="Sword {{ sword_img.item_number }}">
```

### Step 4: Update Admin (Enable Thumbnails)
```python
# projects/admin.py
@admin.register(Sword_img)
class Sword_imgAdmin(admin.ModelAdmin):
    def thumbnail(self, obj):
        if obj.image_file:
            return format_html('<img src="{}" width="40" />', obj.image_file.url)
        elif obj.image and obj.image != "null":
            return format_html('<img src="/media/{}" width="40" />', obj.image)
        return "No image"
    
    thumbnail.short_description = 'Thumbnail'
    list_display = ['item_number', 'thumbnail']
    search_fields = ['item_number']
    list_filter = ['item_number']
```

---

## Option 2: Full Migration (Recommended)

### Step 1: Create Backup
```bash
# Backup database
cp db.sqlite3 db.sqlite3.backup

# Backup media files
cp -r media/ media_backup/
```

### Step 2: Update Models Completely
```python
# projects/models.py
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.html import strip_tags
from ckeditor.fields import RichTextField
from PIL import Image as PILImage
import os

class Sword_img(models.Model):
    item_number = models.IntegerField(default=0)
    image = models.ImageField(upload_to='images/swords/', blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize image if too large
        if self.image:
            img_path = self.image.path
            with PILImage.open(img_path) as img:
                if img.height > 800 or img.width > 800:
                    output_size = (800, 800)
                    img.thumbnail(output_size, PILImage.LANCZOS)
                    img.save(img_path, quality=85, optimize=True)

    def __str__(self):
        return f"Sword {self.item_number}"

class Sword_sales(models.Model):
    item_number = models.IntegerField(default=0)
    image = models.ImageField(upload_to='images/sales/', blank=True, null=True)
    description = models.TextField(blank=True)
    price = models.CharField(max_length=50)
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            img_path = self.image.path
            with PILImage.open(img_path) as img:
                if img.height > 600 or img.width > 600:
                    output_size = (600, 600)
                    img.thumbnail(output_size, PILImage.LANCZOS)
                    img.save(img_path, quality=85, optimize=True)

    def __str__(self):
        return f"Sale Item {self.item_number}"

class BlogImages(models.Model):
    image = models.ImageField(upload_to='images/blog/', blank=True, null=True)
    alt_text = models.CharField(max_length=200, blank=True, help_text="Alternative text for accessibility")
    caption = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Blog Image {self.id}"

class Blog(models.Model):
    date = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=200, blank=True)
    description = RichTextField(blank=True)
    images = models.ManyToManyField(BlogImages, blank=True)
    featured_image = models.ImageField(upload_to='images/blog/featured/', blank=True, null=True)
    is_published = models.BooleanField(default=True)

    @property
    def stripped_rich_field(self):
        return strip_tags(self.description)
    
    def __str__(self):
        return self.title or f"Blog Post {self.date}"

    class Meta:
        ordering = ['-date']
```

### Step 3: Create Migration Script for Data Transfer
```python
# Create a custom migration file: projects/migrations/0999_migrate_image_data.py
from django.db import migrations
import os
from django.conf import settings

def migrate_image_data(apps, schema_editor):
    """Transfer existing image data to new ImageField"""
    Sword_img = apps.get_model('projects', 'Sword_img')
    Sword_sales = apps.get_model('projects', 'Sword_sales')
    BlogImages = apps.get_model('projects', 'BlogImages')
    
    # Migrate Sword_img
    for sword in Sword_img.objects.all():
        if sword.image and sword.image != "null":
            # Check if file exists in media directory
            old_path = os.path.join(settings.MEDIA_ROOT, sword.image)
            if os.path.exists(old_path):
                # Copy file to new location and update field
                # This would need custom logic based on your file structure
                print(f"Would migrate: {sword.image}")
    
    # Similar for other models...

def reverse_migrate_image_data(apps, schema_editor):
    """Reverse migration if needed"""
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('projects', '0998_add_image_fields'),  # Previous migration
    ]

    operations = [
        migrations.RunPython(migrate_image_data, reverse_migrate_image_data),
    ]
```

### Step 4: Update Templates
```html
<!-- projects/templates/projects/gallery.html -->
<div class="card_container">
    {% for sword_img in swords.all %}
    <div class="card" style="width: 18rem;">
        {% if sword_img.image %}
            <img src="{{ sword_img.image.url }}" class="card-img-top" alt="Sword {{ sword_img.item_number }}">
        {% else %}
            <img src="{% static 'images/placeholder.jpg' %}" class="card-img-top" alt="No image available">
        {% endif %}
        <div class="card-body">
            <h5 class="card-title">Sword {{ sword_img.item_number }}</h5>
            <button class="button">
                <a class="button_color" href="{% url 'details_s' sword_img.id %}">Learn more</a>
            </button>
        </div>
    </div>
    {% endfor %}
</div>
```

### Step 5: Update Admin with Enhanced Features
```python
# projects/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Year, Classes, Sword_img, Hotel, Blog, Sword_sales, BlogImages

@admin.register(Sword_img)
class Sword_imgAdmin(admin.ModelAdmin):
    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return "No image"
    thumbnail.short_description = 'Preview'

    def image_info(self, obj):
        if obj.image:
            return format_html(
                '<strong>Size:</strong> {}x{}<br><strong>File:</strong> {:.1f} KB',
                obj.image.width,
                obj.image.height,
                obj.image.size / 1024
            )
        return "No image"
    image_info.short_description = 'Image Info'

    list_display = ['item_number', 'thumbnail', 'image_info', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['item_number', 'description']
    readonly_fields = ['thumbnail', 'image_info', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('item_number', 'description')
        }),
        ('Image', {
            'fields': ('image', 'thumbnail', 'image_info')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(BlogImages)
class BlogImagesAdmin(admin.ModelAdmin):
    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit: cover;" />',
                obj.image.url
            )
        return "No image"
    thumbnail.short_description = 'Preview'

    list_display = ['id', 'thumbnail', 'alt_text', 'created_at']
    list_filter = ['created_at']
    search_fields = ['alt_text', 'caption']
    fields = ['image', 'alt_text', 'caption', 'thumbnail']
    readonly_fields = ['thumbnail']
```

### Step 6: Add Image Upload Forms
```python
# projects/forms.py (create this file)
from django import forms
from .models import Sword_img, Sword_sales, BlogImages

class SwordImageForm(forms.ModelForm):
    class Meta:
        model = Sword_img
        fields = ['item_number', 'image', 'description']
        widgets = {
            'image': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control'
            }),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("Image file too large (max 5MB)")
        return image
```

### Step 7: Update Settings for Production
```python
# omimi/settings.py
# Add at the top
import os
from pathlib import Path

# Add this for image processing
INSTALLED_APPS = [
    # ... existing apps
    'PIL',  # Make sure Pillow is installed: pip install Pillow
]

# Image upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10MB

# For production, uncomment AWS settings and add:
# THUMBNAIL_BACKEND = 'sorl.thumbnail.backends.pil_backend.PILBackend'
```

## Testing the Migration

### Test Checklist:
1. ✅ Images display correctly in gallery
2. ✅ Admin thumbnails work
3. ✅ Image uploads work through admin
4. ✅ Existing images still accessible
5. ✅ No broken links
6. ✅ Performance is acceptable
7. ✅ Mobile responsive still works

### Commands to Run:
```bash
# Install required packages
pip install Pillow

# Create and run migrations
python manage.py makemigrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Test the server
python manage.py runserver
```

## Rollback Plan

If anything goes wrong:
```bash
# Restore database
cp db.sqlite3.backup db.sqlite3

# Restore media files
cp -r media_backup/ media/

# Run server
python manage.py runserver
```

## Next Steps After Migration

1. **Add image validation and processing**
2. **Implement responsive images with multiple sizes**
3. **Add lazy loading for better performance**
4. **Set up CDN for production (AWS CloudFront)**
5. **Add image compression pipeline**
6. **Implement image SEO optimization**

---

## Recommendation

**Start with Option 1 (Quick Fix)** to get immediate benefits with minimal risk, then gradually move to Option 2 for full Django best practices compliance.

This approach gives you:
- ✅ Proper image handling
- ✅ Admin thumbnails
- ✅ Upload validation
- ✅ Automatic URL generation
- ✅ Better organization
- ✅ Production-ready setup