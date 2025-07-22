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
