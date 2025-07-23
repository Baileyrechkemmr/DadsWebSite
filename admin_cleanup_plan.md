# Admin Cleanup Plan

## Safe to Remove: BlogImages
- Legacy blog image management
- Not actively used if AWS blog system is primary

## Steps to Remove BlogImages from Admin:
1. Comment out BlogImages admin registration
2. Test website functionality
3. If no issues, can eventually remove model entirely

## DO NOT REMOVE: Sword_img
- Core functionality for sword gallery
- Used in home page, detail pages, and navigation
- Essential for website operation

## Code Changes Needed:
```python
# In admin.py, comment out or remove:
# @admin.register(BlogImages)
# class BlogImagesAdmin(admin.ModelAdmin):
#     ...

# Also remove from imports:
# from .models import BlogImages
```