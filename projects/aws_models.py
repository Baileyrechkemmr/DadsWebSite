"""
Hybrid Django models that interface with DynamoDB while maintaining Django admin compatibility.
These models act as a bridge between Django's ORM and AWS DynamoDB.
"""

from django.db import models
from django.utils.html import strip_tags
from django.core.exceptions import ObjectDoesNotExist
from ckeditor.fields import RichTextField
from datetime import datetime, timezone
from typing import List, Dict, Optional
import json
import uuid

from .aws_blog_service import blog_service


class DynamoDBBlogPost(models.Model):
    """
    Hybrid model that stores blog posts in DynamoDB but appears as a Django model.
    This allows us to use Django admin interface with DynamoDB backend.
    """
    class Meta:
        managed = False  # Tell Django not to manage this table in SQL database
        verbose_name = "AWS Blog Post"
        verbose_name_plural = "AWS Blog Posts"
    
    # These fields exist for Django admin form rendering
    blog_id = models.CharField(max_length=36, primary_key=True, editable=False)
    title = models.CharField(max_length=200, help_text="Blog post title")
    content = RichTextField(
        default="",
        help_text="Blog post content with rich text formatting"
    )
    image_urls = models.TextField(
        blank=True,
        help_text="JSON array of image URLs (managed automatically)"
    )
    tags = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated tags"
    )
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=True)
    view_count = models.IntegerField(default=0, editable=False)
    
    # Image management (maintains compatibility with existing BlogImages)
    blog_images = models.ManyToManyField(
        'BlogImages',
        blank=True,
        help_text="Upload images for this blog post"
    )
    
    def __str__(self):
        return self.title or f"Blog Post {self.blog_id}"
    
    @property
    def stripped_content(self):
        """Get content without HTML tags"""
        return strip_tags(self.content)
    
    @property
    def image_list(self) -> List[str]:
        """Get list of image URLs"""
        if self.image_urls:
            try:
                return json.loads(self.image_urls)
            except json.JSONDecodeError:
                return []
        return []
    
    def get_tags_list(self) -> List[str]:
        """Get tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def save(self, *args, **kwargs):
        """Override save to store in DynamoDB"""
        # Generate ID if new
        if not self.blog_id:
            self.blog_id = str(uuid.uuid4())
        
        # Collect image URLs from related BlogImages
        image_urls = []
        if self.pk:  # Only if object exists
            for blog_image in self.blog_images.all():
                if blog_image.image:
                    image_urls.append(blog_image.image.url)
        
        # Prepare data for DynamoDB
        blog_data = {
            'title': self.title,
            'content': self.content,
            'images': image_urls,
            'tags': self.get_tags_list(),
            'published': self.published
        }
        
        # Save to DynamoDB
        if hasattr(self, '_state') and self._state.adding:
            # New object
            blog_service.create_blog_post(
                title=self.title,
                content=self.content,
                images=image_urls,
                tags=self.get_tags_list()
            )
        else:
            # Update existing
            blog_service.update_blog_post(self.blog_id, **blog_data)
        
        # Update image_urls field
        self.image_urls = json.dumps(image_urls)
        
        # Don't call super().save() since we're not using SQL database
        # Instead, mark the object as saved
        self._state.adding = False
        self._state.db = 'default'
    
    def delete(self, *args, **kwargs):
        """Override delete to remove from DynamoDB"""
        if self.blog_id:
            blog_service.delete_blog_post(self.blog_id)
        # Don't call super().delete() since we're not using SQL database
    
    @classmethod
    def objects_manager(cls):
        """Custom manager for DynamoDB operations"""
        return DynamoDBBlogPostManager()


class DynamoDBBlogPostManager:
    """Manager for DynamoDB blog post operations"""
    
    def all(self):
        """Get all blog posts from DynamoDB"""
        dynamo_posts = blog_service.get_all_blog_posts()
        return [self._dynamo_to_django(post) for post in dynamo_posts]
    
    def get(self, **kwargs):
        """Get a single blog post"""
        if 'pk' in kwargs:
            blog_id = kwargs['pk']
        elif 'blog_id' in kwargs:
            blog_id = kwargs['blog_id']
        else:
            raise ValueError("Must provide pk or blog_id")
        
        dynamo_post = blog_service.get_blog_post(blog_id)
        if not dynamo_post:
            raise ObjectDoesNotExist("DynamoDBBlogPost matching query does not exist.")
        
        return self._dynamo_to_django(dynamo_post)
    
    def filter(self, **kwargs):
        """Filter blog posts (basic implementation)"""
        all_posts = self.all()
        
        # Basic filtering
        if 'published' in kwargs:
            all_posts = [post for post in all_posts if post.published == kwargs['published']]
        
        return all_posts
    
    def create(self, **kwargs):
        """Create a new blog post"""
        blog_post = DynamoDBBlogPost(**kwargs)
        blog_post.save()
        return blog_post
    
    def _dynamo_to_django(self, dynamo_item: Dict) -> 'DynamoDBBlogPost':
        """Convert DynamoDB item to Django model instance"""
        # Parse datetime strings
        created_date = None
        updated_date = None
        
        if 'created_date' in dynamo_item:
            try:
                created_date = datetime.fromisoformat(dynamo_item['created_date'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                created_date = datetime.now(timezone.utc)
        
        if 'updated_date' in dynamo_item:
            try:
                updated_date = datetime.fromisoformat(dynamo_item['updated_date'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                updated_date = created_date or datetime.now(timezone.utc)
        
        # Create Django model instance
        blog_post = DynamoDBBlogPost(
            blog_id=dynamo_item.get('blog_id', ''),
            title=dynamo_item.get('title', ''),
            content=dynamo_item.get('content', ''),
            image_urls=json.dumps(dynamo_item.get('images', [])),
            tags=', '.join(dynamo_item.get('tags', [])),
            created_date=created_date,
            updated_date=updated_date,
            published=dynamo_item.get('published', True),
            view_count=dynamo_item.get('view_count', 0)
        )
        
        # Mark as not adding (existing record)
        blog_post._state.adding = False
        blog_post._state.db = 'default'
        
        return blog_post


# Custom manager assignment
DynamoDBBlogPost.objects = DynamoDBBlogPostManager()


class BlogImageS3(models.Model):
    """
    Enhanced BlogImages model with better S3 integration
    """
    image = models.ImageField(
        upload_to='blog-images/',
        blank=True,
        null=True,
        help_text="Upload image to S3 bucket"
    )
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Alternative text for accessibility"
    )
    caption = models.TextField(
        blank=True,
        help_text="Image caption (optional)"
    )
    uploaded_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Blog Image (S3)"
        verbose_name_plural = "Blog Images (S3)"
    
    def __str__(self):
        return f"Image {self.id} - {self.alt_text or 'No alt text'}"
    
    @property
    def image_url(self):
        """Get the S3 URL for this image"""
        if self.image:
            return self.image.url
        return None