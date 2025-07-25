from django.contrib import admin
from .models import Year, Classes, Sword_img, Hotel, Blog, Sword_sales, BlogImages, Gallery, OrderSettings
from django.utils.html import format_html
from django.shortcuts import redirect
from django.contrib import messages

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


@admin.register(OrderSettings)
class OrderSettingsAdmin(admin.ModelAdmin):
    def disabled_image_preview(self, obj):
        try:
            if obj.disabled_image and hasattr(obj.disabled_image, 'url'):
                return format_html(
                    '<img src="{}" width="200" height="150" '
                    'style="object-fit: cover; border-radius: 4px;" '
                    'onerror="this.style.display=\'none\'" />', 
                    obj.disabled_image.url
                )
        except Exception as e:
            return f"Image Error: {str(e)[:50]}"
        return "No Image"
    disabled_image_preview.short_description = 'Preview'
    
    def status_display(self, obj):
        if obj.orders_enabled:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Orders Enabled</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Orders Disabled</span>'
            )
    status_display.short_description = 'Status'
    
    def toggle_orders(self, request, queryset):
        """Admin action to quickly toggle order status"""
        for obj in queryset:
            obj.orders_enabled = not obj.orders_enabled
            obj.save()
            status = "enabled" if obj.orders_enabled else "disabled"
            messages.success(request, f'Orders have been {status}!')
    
    toggle_orders.short_description = "Toggle order status (Enable/Disable)"
    
    list_display = ['status_display', 'last_updated']
    readonly_fields = ['disabled_image_preview', 'last_updated']
    actions = ['toggle_orders']
    
    fieldsets = (
        ('Order Control', {
            'fields': ('orders_enabled',),
            'description': 'Use this setting to enable or disable all order functionality across the website.'
        }),
        ('Disabled Orders Display', {
            'fields': ('disabled_message', 'disabled_image', 'disabled_image_preview'),
            'description': 'Configure what visitors see when orders are disabled.'
        }),
        ('System Information', {
            'fields': ('last_updated',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Prevent creating multiple instances (singleton pattern)
        try:
            return not OrderSettings.objects.exists()
        except Exception:
            # During initial deployment, table might not exist yet
            return True
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the settings
        return False
