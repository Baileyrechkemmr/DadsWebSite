"""
Simple AWS-powered blog models using PostgreSQL + S3
Much cleaner and easier to use than DynamoDB approach
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from ckeditor.fields import RichTextField
from django.utils import timezone
import uuid


class BlogCategory(models.Model):
    """Blog categories for organization"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Blog Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogTag(models.Model):
    """Blog tags for detailed categorization"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class SimpleBlogPost(models.Model):
    """Simple, user-friendly blog post model"""
    
    # Core content
    title = models.CharField(
        max_length=200,
        help_text="The title of your blog post"
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        help_text="URL-friendly version of title (auto-generated)"
    )
    content = RichTextField(
        help_text="Write your blog post content here. You can add images, links, and formatting."
    )
    excerpt = models.TextField(
        max_length=300,
        blank=True,
        help_text="Short summary (optional - will be auto-generated if left blank)"
    )
    
    # Featured image
    featured_image = models.ImageField(
        upload_to='blog/featured/',
        blank=True,
        null=True,
        help_text="Main image for your blog post (uploaded to S3)"
    )
    featured_image_alt = models.CharField(
        max_length=200,
        blank=True,
        help_text="Alt text for the featured image (for accessibility)"
    )
    
    # Organization
    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="What category does this post belong to?"
    )
    tags = models.ManyToManyField(
        BlogTag,
        blank=True,
        help_text="Add tags to help readers find your post"
    )
    
    # Publishing
    status_choices = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('scheduled', 'Scheduled'),
    ]
    status = models.CharField(
        max_length=20,
        choices=status_choices,
        default='draft',
        help_text="Is this post ready to be published?"
    )
    
    # Dates
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    publish_date = models.DateTimeField(
        default=timezone.now,
        help_text="When should this post be published?"
    )
    
    # Author (optional - defaults to current user)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=1,
        help_text="Who wrote this post?"
    )
    
    # Metadata
    view_count = models.PositiveIntegerField(default=0, editable=False)
    allow_comments = models.BooleanField(
        default=True,
        help_text="Allow readers to comment on this post?"
    )
    
    # SEO
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Description for search engines (optional)"
    )
    
    class Meta:
        ordering = ['-publish_date']
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Auto-generate slug from title
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while SimpleBlogPost.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        # Auto-generate excerpt if not provided
        if not self.excerpt and self.content:
            # Strip HTML and create excerpt
            from django.utils.html import strip_tags
            clean_content = strip_tags(self.content)
            self.excerpt = clean_content[:297] + "..." if len(clean_content) > 297 else clean_content
        
        # Auto-generate meta description if not provided
        if not self.meta_description:
            self.meta_description = self.excerpt[:157] + "..." if len(self.excerpt) > 157 else self.excerpt
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('simple_blog_detail', kwargs={'slug': self.slug})
    
    @property
    def is_published(self):
        return (
            self.status == 'published' and 
            self.publish_date <= timezone.now()
        )
    
    @property
    def reading_time(self):
        """Estimate reading time in minutes"""
        from django.utils.html import strip_tags
        word_count = len(strip_tags(self.content).split())
        return max(1, round(word_count / 200))  # Assume 200 words per minute
    
    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])


class BlogImage(models.Model):
    """Additional images that can be embedded in blog posts"""
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(
        upload_to='blog/images/',
        help_text="Upload image to S3"
    )
    alt_text = models.CharField(
        max_length=200,
        help_text="Alternative text for accessibility"
    )
    caption = models.TextField(blank=True)
    uploaded_date = models.DateTimeField(auto_now_add=True)
    
    # Link to blog posts
    blog_posts = models.ManyToManyField(
        SimpleBlogPost,
        blank=True,
        related_name='additional_images'
    )
    
    class Meta:
        ordering = ['-uploaded_date']
    
    def __str__(self):
        return self.title or f"Image {self.id}"
    
    @property
    def image_url(self):
        """Get the S3 URL for this image"""
        return self.image.url if self.image else None


class BlogComment(models.Model):
    """Simple comment system (optional)"""
    blog_post = models.ForeignKey(
        SimpleBlogPost,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_date']
    
    def __str__(self):
        return f"Comment by {self.author_name} on {self.blog_post.title}"