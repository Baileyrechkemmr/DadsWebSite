"""
Django admin interface for DynamoDB-backed blog posts.
This provides a familiar Django admin experience while storing data in AWS.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from .aws_models import DynamoDBBlogPost, BlogImageS3
from .models import BlogImages  # Keep existing BlogImages for compatibility
import json


class BlogImageS3Inline(admin.TabularInline):
    """Inline admin for blog images"""
    model = BlogImageS3
    extra = 1
    fields = ['image', 'alt_text', 'caption']
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # Make images optional in inline
        formset.form.base_fields['image'].required = False
        return formset


@admin.register(DynamoDBBlogPost)
class DynamoDBBlogPostAdmin(admin.ModelAdmin):
    """Admin interface for DynamoDB blog posts"""
    
    # Display configuration
    list_display = ['title', 'created_date_display', 'published', 'view_count', 'preview_content']
    list_filter = ['published', 'created_date']
    search_fields = ['title', 'content']
    date_hierarchy = 'created_date'
    
    # Form configuration
    fields = [
        'title', 
        'content', 
        'tags', 
        'published', 
        'blog_images',  # Many-to-many field for images
        'preview_images'  # Read-only preview of current images
    ]
    
    filter_horizontal = ['blog_images']  # Nice widget for many-to-many
    readonly_fields = ['preview_images', 'view_count', 'created_date', 'updated_date']
    
    # Custom form layout
    fieldsets = (
        ('Content', {
            'fields': ('title', 'content', 'tags')
        }),
        ('Images', {
            'fields': ('blog_images', 'preview_images'),
            'description': 'Upload and manage images for this blog post'
        }),
        ('Publishing', {
            'fields': ('published',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('view_count', 'created_date', 'updated_date'),
            'classes': ('collapse',),
            'description': 'Automatically managed fields'
        })
    )
    
    # Make content field larger
    formfield_overrides = {
        # Content field will use CKEditor from the model definition
    }
    
    def get_queryset(self, request):
        """Get queryset from DynamoDB"""
        try:
            return DynamoDBBlogPost.objects.all()
        except Exception as e:
            messages.error(request, f"Error loading blog posts from DynamoDB: {e}")
            return []
    
    def get_object(self, request, object_id, from_field=None):
        """Get single object from DynamoDB"""
        try:
            return DynamoDBBlogPost.objects.get(pk=object_id)
        except Exception as e:
            messages.error(request, f"Error loading blog post: {e}")
            return None
    
    def save_model(self, request, obj, form, change):
        """Save model to DynamoDB"""
        try:
            obj.save()
            if change:
                messages.success(request, f'Blog post "{obj.title}" was updated successfully in DynamoDB.')
            else:
                messages.success(request, f'Blog post "{obj.title}" was created successfully in DynamoDB.')
        except Exception as e:
            messages.error(request, f'Error saving blog post: {e}')
            raise
    
    def delete_model(self, request, obj):
        """Delete model from DynamoDB"""
        try:
            obj.delete()
            messages.success(request, f'Blog post "{obj.title}" was deleted successfully from DynamoDB.')
        except Exception as e:
            messages.error(request, f'Error deleting blog post: {e}')
            raise
    
    def delete_queryset(self, request, queryset):
        """Bulk delete from DynamoDB"""
        deleted_count = 0
        for obj in queryset:
            try:
                obj.delete()
                deleted_count += 1
            except Exception as e:
                messages.error(request, f'Error deleting "{obj.title}": {e}')
        
        if deleted_count > 0:
            messages.success(request, f'Successfully deleted {deleted_count} blog posts from DynamoDB.')
    
    # Custom display methods
    def created_date_display(self, obj):
        """Format created date"""
        if obj.created_date:
            return obj.created_date.strftime('%Y-%m-%d %H:%M')
        return 'Unknown'
    created_date_display.short_description = 'Created'
    created_date_display.admin_order_field = 'created_date'
    
    def preview_content(self, obj):
        """Show content preview"""
        if obj.content:
            preview = obj.stripped_content[:100]
            if len(obj.stripped_content) > 100:
                preview += '...'
            return preview
        return 'No content'
    preview_content.short_description = 'Content Preview'
    
    def preview_images(self, obj):
        """Show preview of current images"""
        if not obj.pk:
            return 'Save the blog post first to see images'
        
        html_parts = []
        
        # Show images from blog_images many-to-many relationship
        for blog_image in obj.blog_images.all():
            if blog_image.image:
                html_parts.append(
                    f'<div style="display: inline-block; margin: 5px; text-align: center;">' +
                    f'<img src="{blog_image.image.url}" style="max-width: 100px; max-height: 100px; border-radius: 4px;" />' +
                    f'<br><small>ID: {blog_image.id}</small>' +
                    f'</div>'
                )
        
        # Also show any images from DynamoDB (for consistency)
        image_list = obj.image_list
        for i, img_url in enumerate(image_list):
            html_parts.append(
                f'<div style="display: inline-block; margin: 5px; text-align: center;">' +
                f'<img src="{img_url}" style="max-width: 100px; max-height: 100px; border-radius: 4px;" />' +
                f'<br><small>DDB Image {i+1}</small>' +
                f'</div>'
            )
        
        if not html_parts:
            return 'No images uploaded'
        
        return format_html('<div style="max-width: 600px;">' + ''.join(html_parts) + '</div>')
    
    preview_images.short_description = 'Current Images'
    
    # Custom actions
    actions = ['make_published', 'make_unpublished']
    
    def make_published(self, request, queryset):
        """Publish selected blog posts"""
        updated = 0
        for obj in queryset:
            try:
                obj.published = True
                obj.save()
                updated += 1
            except Exception as e:
                messages.error(request, f'Error publishing "{obj.title}": {e}')
        
        if updated > 0:
            messages.success(request, f'Successfully published {updated} blog posts.')
    
    make_published.short_description = "Publish selected blog posts"
    
    def make_unpublished(self, request, queryset):
        """Unpublish selected blog posts"""
        updated = 0
        for obj in queryset:
            try:
                obj.published = False
                obj.save()
                updated += 1
            except Exception as e:
                messages.error(request, f'Error unpublishing "{obj.title}": {e}')
        
        if updated > 0:
            messages.success(request, f'Successfully unpublished {updated} blog posts.')
    
    make_unpublished.short_description = "Unpublish selected blog posts"
    
    # Custom URLs for additional functionality
    def get_urls(self):
        urls = super().get_urls()
        from django.urls import path
        custom_urls = [
            path('<path:object_id>/preview/', self.admin_site.admin_view(self.preview_view), name='aws_blog_preview'),
        ]
        return custom_urls + urls
    
    def preview_view(self, request, object_id):
        """Preview blog post"""
        try:
            obj = self.get_object(request, object_id)
            if obj:
                # Increment view count
                from .aws_blog_service import blog_service
                blog_service.increment_view_count(obj.blog_id)
                
                # You could render a preview template here
                # For now, redirect to the change view
                messages.info(request, f'Preview accessed for "{obj.title}" (view count incremented)')
            return HttpResponseRedirect(reverse('admin:projects_dynamodblogpost_change', args=[object_id]))
        except Exception as e:
            messages.error(request, f'Error previewing blog post: {e}')
            return HttpResponseRedirect(reverse('admin:projects_dynamodblogpost_changelist'))


@admin.register(BlogImageS3)
class BlogImageS3Admin(admin.ModelAdmin):
    """Admin for S3 blog images"""
    
    list_display = ['thumbnail', 'alt_text', 'uploaded_date', 'image_url_display']
    list_filter = ['uploaded_date']
    search_fields = ['alt_text', 'caption']
    readonly_fields = ['thumbnail', 'uploaded_date']
    
    def thumbnail(self, obj):
        """Show thumbnail preview"""
        if obj.image:
            return format_html(
                '<img src="{}" width="80" height="60" style="object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "No Image"
    thumbnail.short_description = 'Preview'
    
    def image_url_display(self, obj):
        """Show S3 URL"""
        if obj.image:
            url = obj.image.url
            return format_html('<a href="{}" target="_blank">{}</a>', url, url[:50] + '...' if len(url) > 50 else url)
        return 'No URL'
    image_url_display.short_description = 'S3 URL'