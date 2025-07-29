from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.html import strip_tags
from ckeditor.fields import RichTextField
# Create your models here.
#what u added at the admin page path



class Year(models.Model):
    title = models.CharField(default="year", max_length=4)
    class_year = models.IntegerField()

    def __str__(self):
        return self.title

class Classes(models.Model):
    class_title = models.CharField(max_length=250)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(default="null")
    class_slots = models.IntegerField(default=0)

    def __str__(self):
        return self.class_title
# ask dad about price and if yes add price felid

class Sword_img(models.Model):
    item_number = models.IntegerField(default=0)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    description = models.TextField(default="null")

    def __str__(self):
        return str(self.item_number)


# at a later date have a felid possibly to use for the card for the travel and logins information 
class Hotel(models.Model):
    city_name = models.CharField(max_length=100)
    hotel_name = models.CharField(max_length=250)
    address = models.CharField(max_length=100)
    description = models.TextField(default="null")
    distance = models.CharField(max_length=100)
    phone = models.CharField(max_length=100, default="515-555-5555")

    def __str__(self):
        return self.hotel_name


class Sword_sales(models.Model):
    item_number = models.IntegerField(default=0)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    description = models.TextField(default="null")
    price = models.CharField(max_length=50)

    def __str__(self):
        return str(self.item_number)

# admin feild for blog posts

class BlogImages(models.Model):
    image = models.ImageField(upload_to='images/', blank=True, null=True)


class Blog(models.Model):
    date = models.DateField(auto_now_add=True)
    description = RichTextField(default="null")
    images = models.ManyToManyField(BlogImages, blank=True)

    @property
    def stripped_rich_field(self):
        return strip_tags(self.description)
    
    class Meta:
        ordering = ['-date']  # Show newest posts first
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
    
    def __str__(self):
        # Create a more descriptive name using date and a snippet of content
        content_snippet = self.stripped_rich_field[:50] if self.stripped_rich_field else "No content"
        return f"Blog Post - {self.date.strftime('%B %d, %Y')} - {content_snippet}..."


class Gallery(models.Model):
    """
    Dedicated model for managing gallery images.
    Only images added here will appear in the gallery page.
    """
    title = models.CharField(max_length=200, help_text="Title for the gallery image")
    image = models.ImageField(upload_to='images/gallery/', blank=False, null=False)
    description = models.TextField(blank=True, help_text="Optional description for the image")
    is_active = models.BooleanField(default=True, help_text="Uncheck to hide from gallery")
    sort_order = models.IntegerField(default=0, help_text="Lower numbers appear first")
    date_added = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['sort_order', '-date_added']
        verbose_name = 'Gallery Image'
        verbose_name_plural = 'Gallery Images'
    
    def __str__(self):
        return self.title


class OrderSettings(models.Model):
    """
    Singleton model to control order functionality site-wide.
    Only one instance should exist.
    """
    orders_enabled = models.BooleanField(
        default=True, 
        help_text="Uncheck to disable all order functionality and show 'no longer accepting orders' message"
    )
    disabled_message = models.TextField(
        default="No longer accepting orders at this time",
        help_text="Message to display when orders are disabled"
    )
    disabled_image = models.ImageField(
        upload_to='images/system/', 
        blank=True, 
        null=True,
        help_text="Optional image to display when orders are disabled"
    )
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Order Settings'
        verbose_name_plural = 'Order Settings'
    
    def __str__(self):
        status = "Enabled" if self.orders_enabled else "Disabled"
        return f"Order Settings - {status}"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton pattern)
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class PageContent(models.Model):
    """
    Model for managing editable text content across different pages.
    Allows admins to edit text content without touching HTML templates.
    """
    PAGE_CHOICES = [
        # Sales Page
        ('sales_paypal_info', 'Sales Page - PayPal Information'),
        ('sales_form_title', 'Sales Page - Form Title'),
        
        # Footer & Coming Soon (appears on all pages)
        ('footer_copyright', 'Footer - Copyright Text'),
        ('coming_soon_title', 'Coming Soon - Title'),
        ('coming_soon_message', 'Coming Soon - Message'),
        
        # Home Page Content
        ('home_classes_description', 'Home Page - Classes Description'),
        ('home_l6_video_description', 'Home Page - L6 Video Description'),
        ('home_blog_description', 'Home Page - Blog Description'),
        
        # About Page
        ('about_biography', 'About Page - Howard Clark Biography'),
        
        # Order Form Page
        ('order_paypal_instructions', 'Order Form - PayPal Instructions'),
        ('order_rules_section', 'Order Form - Rules & Pricing'),
        
        # Classes Page
        ('classes_general_info', 'Classes Page - General Information'),
        ('classes_payment_instructions', 'Classes Page - Payment Instructions'),
        ('classes_address_info', 'Classes Page - Address Information'),
        ('classes_materials_info', 'Classes Page - Materials Information'),
        ('classes_equipment_requirements', 'Classes Page - Equipment Requirements'),
        ('classes_safety_equipment', 'Classes Page - Safety Equipment'),
        ('classes_practice_recommendations', 'Classes Page - Practice Recommendations'),
        ('classes_one_on_one_info', 'Classes Page - One-on-One Lessons'),
        
        # Orders Disabled Page
        ('orders_disabled_title', 'Orders Disabled - Title'),
        ('orders_disabled_message', 'Orders Disabled - Message'),
    ]
    
    page_section = models.CharField(
        max_length=50, 
        choices=PAGE_CHOICES, 
        unique=True,
        help_text="Select which section of the website this content belongs to"
    )
    title = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Optional title for this content section"
    )
    content = models.TextField(
        help_text="The actual content that will be displayed on the website"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this content from the website"
    )
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Page Content'
        verbose_name_plural = 'Page Content'
        ordering = ['page_section']
    
    def __str__(self):
        return f"{self.get_page_section_display()} - {self.title or 'No title'}"
    
    @classmethod
    def get_content(cls, page_section, default_content=""):
        """
        Get content for a specific page section.
        Returns the content if found and active, otherwise returns default_content.
        """
        try:
            content_obj = cls.objects.get(page_section=page_section, is_active=True)
            return content_obj.content
        except cls.DoesNotExist:
            return default_content
