# Django S3 Optimization Plan for Omimi Swords

## Current Situation ✅
- **S3 bucket active**: `ominisword-images` with 1000+ files
- **AWS credentials configured**: Working S3 connection
- **Images already uploaded**: 122+ image files in various folders
- **Django-storages installed**: Ready for proper integration

## Issues to Fix ❌
1. **Models use CharField instead of ImageField**
2. **Templates manually construct URLs** 
3. **No admin upload interface**
4. **Files scattered across prefixes**
5. **S3 settings commented out in Django**

## Phase 1: Enable S3 in Django Settings

### Update settings.py
```python
# omimi/settings.py
import os

# Enable S3 storage in production
USE_S3 = os.environ.get('USE_S3', 'True') == 'True'

if USE_S3:
    # AWS S3 Settings
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION', 'us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_DEFAULT_ACL = None  # Use bucket default (no ACLs)
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }

    # S3 Media Settings
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
    
    # S3 Static Settings (optional - you already have staticfiles there)
    STATICFILES_STORAGE = 'storages.backends.s3boto3.StaticS3Boto3Storage'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
else:
    # Local development
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
    STATIC_URL = '/static/'
```

## Phase 2: Fix Django Models

### Update models.py
```python
# projects/models.py
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from ckeditor.fields import RichTextField

class Sword_img(models.Model):
    item_number = models.IntegerField(default=0, unique=True)
    # Change from CharField to ImageField
    image = models.ImageField(upload_to='gallery/swords/', blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sword {self.item_number}"

class Sword_sales(models.Model):
    item_number = models.IntegerField(default=0, unique=True)
    # Change from CharField to ImageField  
    image = models.ImageField(upload_to='gallery/sales/', blank=True, null=True)
    description = models.TextField(blank=True)
    price = models.CharField(max_length=50)
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale Item {self.item_number}"

class BlogImages(models.Model):
    # Change from CharField to ImageField
    image = models.ImageField(upload_to='blog/', blank=True, null=True)
    alt_text = models.CharField(max_length=200, blank=True)
    caption = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Blog Image {self.id}"

class Blog(models.Model):
    title = models.CharField(max_length=200, blank=True)
    date = models.DateField(auto_now_add=True)
    description = RichTextField(blank=True)
    images = models.ManyToManyField(BlogImages, blank=True)
    # Add featured image
    featured_image = models.ImageField(upload_to='blog/featured/', blank=True, null=True)
    is_published = models.BooleanField(default=True)

    @property
    def stripped_rich_field(self):
        return strip_tags(self.description)
    
    def __str__(self):
        return self.title or f"Blog Post {self.date}"

    class Meta:
        ordering = ['-date']
```

## Phase 3: Map Existing S3 Files to Models

### Data Migration Script
```python
# Link existing S3 images to your models
def link_existing_s3_images():
    # For sword images
    sword = Sword_img.objects.get_or_create(item_number=1)[0]
    sword.image = 'images/sword_one.webp'  # Existing S3 path
    sword.save()
    
    # For blog images - link existing S3 files
    # This connects your current S3 files to Django models
```

## Phase 4: Update Templates

### Fix gallery.html
```html
<!-- Change from manual URL construction -->
<!-- OLD: <img src="{{ MEDIA_URL }}{{ sword_img.image }}" class="card-img-top"> -->

<!-- NEW: Use ImageField URL -->
{% if sword_img.image %}
    <img src="{{ sword_img.image.url }}" class="card-img-top" alt="Sword {{ sword_img.item_number }}">
{% else %}
    <img src="{% static 'images/placeholder.jpg' %}" class="card-img-top" alt="No image available">
{% endif %}
```

## Phase 5: Enable Admin Upload Interface

### Enhanced admin.py
```python
# projects/admin.py
@admin.register(Sword_img)
class Sword_imgAdmin(admin.ModelAdmin):
    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="80" height="80" style="object-fit: cover; border-radius: 8px;" />',
                obj.image.url
            )
        return "No image"
    thumbnail.short_description = 'Preview'

    list_display = ['item_number', 'thumbnail', 'description', 'created_at']
    fields = ['item_number', 'image', 'description', 'thumbnail']
    readonly_fields = ['thumbnail', 'created_at', 'updated_at']
```

## Phase 6: Test the Integration

### Verification Steps
1. ✅ S3 URLs work in templates
2. ✅ Admin shows thumbnails  
3. ✅ New uploads go to S3
4. ✅ Images display correctly
5. ✅ No broken links

## Expected Benefits

**After optimization:**
- ✅ **Admin upload interface** with thumbnails
- ✅ **Automatic S3 uploads** for new images
- ✅ **Proper Django ImageField benefits**
- ✅ **Clean template code**
- ✅ **Professional image management**
- ✅ **Better organization** for new uploads

## Sample S3 URLs (Already Working!)
- https://ominisword-images.s3.us-east-1.amazonaws.com/images/sword_one.webp
- https://ominisword-images.s3.us-east-1.amazonaws.com/static/blog.png
- https://ominisword-images.s3.us-east-1.amazonaws.com/images/100_3589.png

## Timeline
- **Phase 1-2**: 30 minutes (settings + models)
- **Phase 3**: 15 minutes (link existing files)  
- **Phase 4-5**: 30 minutes (templates + admin)
- **Phase 6**: 15 minutes (testing)
- **Total**: ~90 minutes

**Ready to proceed with the optimization?**