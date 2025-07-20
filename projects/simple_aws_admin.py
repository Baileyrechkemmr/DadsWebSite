"""
User-friendly Django admin for AWS blog
Designed for non-technical users who just want to write blog posts
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone
from .simple_aws_models import SimpleBlogPost, BlogCategory, BlogTag, BlogImage, BlogComment


# Inline admin for additional images
class BlogImageInline(admin.TabularInline):
    model = BlogImage.blog_posts.through
    extra = 0
    verbose_name = "Additional Image"
    verbose_name_plural = "Additional Images (Optional)"


@admin.register(SimpleBlogPost)
class SimpleBlogPostAdmin(admin.ModelAdmin):
    """Super user-friendly blog post admin"""
    
    # What appears in the blog post list
    list_display = [
        'title', 
        'status_badge', 
        'category', 
        'publish_date_display', 
        'view_count_display',
        'featured_image_preview'
    ]
    
    # Filters on the right side
    list_filter = [
        'status', 
        'category', 
        'tags', 
        'publish_date',
        'created_date'
    ]
    
    # Search functionality
    search_fields = ['title', 'content', 'excerpt']
    
    # Date navigation
    date_hierarchy = 'publish_date'
    
    # How many posts per page
    list_per_page = 20
    
    # Pre-populate slug from title
    prepopulated_fields = {'slug': ('title',)}
    
    # Auto-complete for tags
    filter_horizontal = ['tags']
    
    # Include additional images
    inlines = [BlogImageInline]
    
    # Form layout - organized for ease of use
    fieldsets = (
        ('✍️ Write Your Post', {
            'fields': (
                'title',
                'content',
                'excerpt',
            ),
            'description': 'Start here! Write your blog post title and content.'
        }),
        
        ('🖼️ Images', {
            'fields': (
                'featured_image',
                'featured_image_alt',
            ),
            'description': 'Upload a main image for your post (optional but recommended).'
        }),
        
        ('🏷️ Organization', {
            'fields': (
                'category',
                'tags',
            ),
            'description': 'Help readers find your post by adding a category and tags.'
        }),
        
        ('📅 Publishing', {
            'fields': (
                'status',
                'publish_date',
                'allow_comments',
            ),
            'description': 'Control when and how your post is published.'
        }),
        
        ('🔍 SEO (Optional)', {
            'fields': (
                'meta_description',
            ),
            'classes': ('collapse',),
            'description': 'Optional settings to help search engines understand your post.'
        }),
        
        ('⚙️ Advanced', {
            'fields': (
                'slug',
                'author',
            ),
            'classes': ('collapse',),
            'description': 'These are usually auto-generated, but you can customize them.'
        })
    )
    
    # Read-only fields
    readonly_fields = ['view_count', 'created_date', 'updated_date']
    
    # Default values for new posts
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # New post
            form.base_fields['author'].initial = request.user
            form.base_fields['publish_date'].initial = timezone.now()
        return form
    
    # Custom display methods
    def status_badge(self, obj):
        colors = {
            'draft': '#ffc107',      # Yellow
            'published': '#28a745',   # Green  
            'scheduled': '#007bff',   # Blue
        }
        color = colors.get(obj.status, '#6c757d')
        
        if obj.status == 'scheduled' and obj.publish_date > timezone.now():
            status_text = f"Scheduled for {obj.publish_date.strftime('%b %d')}"
        else:
            status_text = obj.get_status_display()
            
        return format_html(
            '<span style=\"background: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.8em;\">{}</span>',
            color, status_text
        )\n    status_badge.short_description = 'Status'\n    status_badge.admin_order_field = 'status'\n    \n    def publish_date_display(self, obj):\n        if obj.publish_date:\n            if obj.publish_date.date() == timezone.now().date():\n                return f\"Today at {obj.publish_date.strftime('%H:%M')}\"\n            elif obj.publish_date > timezone.now():\n                return f\"📅 {obj.publish_date.strftime('%b %d, %Y')}\"\n            else:\n                return obj.publish_date.strftime('%b %d, %Y')\n        return 'No date set'\n    publish_date_display.short_description = 'Publish Date'\n    publish_date_display.admin_order_field = 'publish_date'\n    \n    def view_count_display(self, obj):\n        if obj.view_count > 0:\n            return f\"👁️ {obj.view_count}\"\n        return \"No views yet\"\n    view_count_display.short_description = 'Views'\n    view_count_display.admin_order_field = 'view_count'\n    \n    def featured_image_preview(self, obj):\n        if obj.featured_image:\n            return format_html(\n                '<img src=\"{}\" width=\"50\" height=\"50\" style=\"object-fit: cover; border-radius: 4px;\" />',\n                obj.featured_image.url\n            )\n        return \"📷 No image\"\n    featured_image_preview.short_description = 'Image'\n    \n    # Custom actions\n    actions = ['publish_posts', 'draft_posts', 'duplicate_post']\n    \n    def publish_posts(self, request, queryset):\n        updated = queryset.update(status='published', publish_date=timezone.now())\n        self.message_user(request, f'Successfully published {updated} blog posts.', messages.SUCCESS)\n    publish_posts.short_description = \"✅ Publish selected posts now\"\n    \n    def draft_posts(self, request, queryset):\n        updated = queryset.update(status='draft')\n        self.message_user(request, f'Moved {updated} blog posts to draft.', messages.SUCCESS)\n    draft_posts.short_description = \"📝 Move to draft\"\n    \n    def duplicate_post(self, request, queryset):\n        for post in queryset:\n            post.pk = None\n            post.title = f\"Copy of {post.title}\"\n            post.slug = None  # Will be auto-generated\n            post.status = 'draft'\n            post.save()\n        self.message_user(request, f'Created {queryset.count()} duplicate posts as drafts.', messages.SUCCESS)\n    duplicate_post.short_description = \"📋 Duplicate as draft\"\n    \n    # Custom save behavior\n    def save_model(self, request, obj, form, change):\n        if not change:  # New post\n            obj.author = request.user\n        super().save_model(request, obj, form, change)\n        \n        # Show helpful message\n        if obj.status == 'published':\n            messages.success(request, f'🎉 Your blog post \"{obj.title}\" is now live!')\n        elif obj.status == 'scheduled':\n            messages.info(request, f'📅 Your blog post \"{obj.title}\" is scheduled to publish on {obj.publish_date.strftime(\"%B %d, %Y\")}')\n        else:\n            messages.info(request, f'📝 Your blog post \"{obj.title}\" has been saved as a draft.')\n\n\n@admin.register(BlogCategory)\nclass BlogCategoryAdmin(admin.ModelAdmin):\n    \"\"\"Simple category management\"\"\"\n    list_display = ['name', 'post_count', 'created_date']\n    prepopulated_fields = {'slug': ('name',)}\n    search_fields = ['name', 'description']\n    \n    def post_count(self, obj):\n        count = obj.simpleblogpost_set.count()\n        return f\"📝 {count} posts\" if count > 0 else \"No posts yet\"\n    post_count.short_description = 'Posts'\n\n\n@admin.register(BlogTag)\nclass BlogTagAdmin(admin.ModelAdmin):\n    \"\"\"Simple tag management\"\"\"\n    list_display = ['name', 'post_count']\n    prepopulated_fields = {'slug': ('name',)}\n    search_fields = ['name']\n    \n    def post_count(self, obj):\n        count = obj.simpleblogpost_set.count()\n        return f\"🏷️ {count} posts\" if count > 0 else \"No posts yet\"\n    post_count.short_description = 'Used in'\n\n\n@admin.register(BlogImage)\nclass BlogImageAdmin(admin.ModelAdmin):\n    \"\"\"Manage blog images\"\"\"\n    list_display = ['image_preview', 'title', 'alt_text', 'uploaded_date', 'usage_count']\n    list_filter = ['uploaded_date']\n    search_fields = ['title', 'alt_text', 'caption']\n    filter_horizontal = ['blog_posts']\n    \n    def image_preview(self, obj):\n        if obj.image:\n            return format_html(\n                '<img src=\"{}\" width=\"60\" height=\"60\" style=\"object-fit: cover; border-radius: 4px;\" />',\n                obj.image.url\n            )\n        return \"No image\"\n    image_preview.short_description = 'Preview'\n    \n    def usage_count(self, obj):\n        count = obj.blog_posts.count()\n        return f\"Used in {count} posts\" if count > 0 else \"Not used yet\"\n    usage_count.short_description = 'Usage'\n\n\n@admin.register(BlogComment)\nclass BlogCommentAdmin(admin.ModelAdmin):\n    \"\"\"Moderate blog comments\"\"\"\n    list_display = ['author_name', 'blog_post', 'created_date', 'is_approved', 'content_preview']\n    list_filter = ['is_approved', 'created_date', 'blog_post']\n    search_fields = ['author_name', 'author_email', 'content']\n    actions = ['approve_comments', 'unapprove_comments']\n    \n    def content_preview(self, obj):\n        return obj.content[:50] + \"...\" if len(obj.content) > 50 else obj.content\n    content_preview.short_description = 'Comment'\n    \n    def approve_comments(self, request, queryset):\n        updated = queryset.update(is_approved=True)\n        self.message_user(request, f'Approved {updated} comments.', messages.SUCCESS)\n    approve_comments.short_description = \"✅ Approve selected comments\"\n    \n    def unapprove_comments(self, request, queryset):\n        updated = queryset.update(is_approved=False)\n        self.message_user(request, f'Unapproved {updated} comments.', messages.SUCCESS)\n    unapprove_comments.short_description = \"❌ Unapprove selected comments\"\n\n\n# Customize admin site header\nadmin.site.site_header = \"Omimi Blog Administration\"\nadmin.site.site_title = \"Omimi Blog Admin\"\nadmin.site.index_title = \"Welcome to your blog dashboard\""