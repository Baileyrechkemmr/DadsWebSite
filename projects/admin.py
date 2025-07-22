from django.contrib import admin
from .models import Year, Classes, Sword_img, Hotel, Blog, Sword_sales, BlogImages, Gallery
from django.utils.html import format_html

# Import AWS models and admin - temporarily disabled to test S3 images
# from .aws_models import DynamoDBBlogPost, BlogImageS3
# from .aws_admin import DynamoDBBlogPostAdmin, BlogImageS3Admin

# Register your models here.
# for admin page

# AWS models are registered in aws_admin.py
# This maintains compatibility with existing models


@admin.register(Year)
class YearAdmin(admin.ModelAdmin):
    list_display = ['class_year']
    search_fields = ['class_year']
    list_filter = ['class_year']


@admin.register(Classes)  # can also add a date time filter
class ClassesAdmin(admin.ModelAdmin):
    list_display = ['class_title']
    search_fields = ['class_title']
    list_filter = ['class_title']


@admin.register(Sword_img)
class Sword_imgAdmin(admin.ModelAdmin):
    # def thumbnail(self, object):
    #     return format_html('<img src="{}" width="40" />'.format(object.image.url))
    
    # list_display = ['item_number', 'thumbnail']
    list_display = ['item_number']
    search_fields = ['item_number']
    list_filter = ['item_number']


@admin.register(Sword_sales)
class Sword_salesAdmin(admin.ModelAdmin):
    def thumbnail(self, obj):
        try:
            if obj.image and hasattr(obj.image, 'url'):
                return format_html(
                    '<img src="{}" width="50" height="50" '
                    'style="object-fit: cover; border-radius: 4px;" '
                    'onerror="this.style.display=\'none\'" />', 
                    obj.image.url
                )
        except Exception as e:
            return f"Image Error: {str(e)[:50]}"
        return "No Image"
    thumbnail.short_description = 'Preview'

    list_display = ['item_number', 'thumbnail', 'price', 'description']
    search_fields = ['item_number', 'description', 'price']
    list_filter = ['item_number']
    readonly_fields = ['thumbnail']

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['hotel_name', 'phone']
    search_fields = ['hotel_name']
    list_filter = ['hotel_name']


class BlogImagesInline(admin.TabularInline):
    model = Blog.images.through


@admin.register(BlogImages)
class BlogImagesAdmin(admin.ModelAdmin):
    def thumbnail(self, obj):
        try:
            if obj.image and hasattr(obj.image, 'url'):
                return format_html(
                    '<img src="{}" width="80" height="60" '
                    'style="object-fit: cover; border-radius: 4px;" '
                    'onerror="this.style.display=\'none\'" />', 
                    obj.image.url
                )
        except Exception as e:
            return f"Image Error: {str(e)[:50]}"
        return "No Image"
    thumbnail.short_description = 'Preview'
    
    list_display = ['thumbnail', 'image']
    readonly_fields = ['thumbnail']


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    def content_preview(self, obj):
        """Show a preview of the blog content"""
        content = obj.stripped_rich_field
        if content and content != "null":
            return content[:100] + "..." if len(content) > 100 else content
        return "No content"
    content_preview.short_description = 'Content Preview'
    
    def formatted_date(self, obj):
        """Show a nicely formatted date"""
        return obj.date.strftime('%B %d, %Y (%A)')
    formatted_date.short_description = 'Date Created'
    formatted_date.admin_order_field = 'date'
    
    list_display = ['formatted_date', 'content_preview']
    search_fields = ['description', 'date']
    list_filter = ['date']
    readonly_fields = ['date']  # Make date readonly since it's auto-generated
    inlines = [BlogImagesInline]
    
    # Show newest posts first
    ordering = ['-date']
    
    fieldsets = (
        ('Blog Content', {
            'fields': ('description',)
        }),
        ('Metadata', {
            'fields': ('date',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    def thumbnail(self, obj):
        try:
            if obj.image and hasattr(obj.image, 'url'):
                return format_html(
                    '<img src="{}" width="80" height="60" '
                    'style="object-fit: cover; border-radius: 4px;" '
                    'onerror="this.style.display=\'none\'" />', 
                    obj.image.url
                )
        except Exception as e:
            return f"Image Error: {str(e)[:50]}"
        return "No Image"
    thumbnail.short_description = 'Preview'
    
    list_display = ['title', 'thumbnail', 'is_active', 'sort_order', 'date_added']
    list_filter = ['is_active', 'date_added']
    search_fields = ['title', 'description']
    list_editable = ['is_active', 'sort_order']
    readonly_fields = ['thumbnail', 'date_added']
    
    fieldsets = (
        ('Image Information', {
            'fields': ('title', 'image', 'thumbnail', 'description')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'sort_order')
        }),
        ('Metadata', {
            'fields': ('date_added',),
            'classes': ('collapse',)
        }),
    )
