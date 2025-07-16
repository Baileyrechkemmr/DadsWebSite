from django.contrib import admin
from .models import Year, Classes, Sword_img, Hotel, Blog, Sword_sales, BlogImages
from django.utils.html import format_html
# Register your models here.
# for admin page

# samm as in modles.py for name and what not


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
    # def thumbnail(self, object):
    #     return format_html('<img src="{}" width="40" />'.format(object.image.url))

    # list_display = ['item_number', 'thumbnail']
    list_display = ['item_number']
    search_fields = ['item_number']
    list_filter = ['item_number']

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['hotel_name', 'phone']
    search_fields = ['hotel_name']
    list_filter = ['hotel_name']


class BlogImagesInline(admin.TabularInline):
    model = Blog.images.through


@admin.register(BlogImages)
class BlogImagesAdmin(admin.ModelAdmin):
    list_display = ['image']


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['date']
    search_fields = ['date']
    list_filter = ['date']
    inlines = [BlogImagesInline]
