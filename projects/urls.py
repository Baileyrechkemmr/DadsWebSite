"""
URL patterns for the projects app with AWS blog integration.
"""

from django.urls import path
from . import views, simple_views

urlpatterns = [
    # Existing URLs
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('classes/', views.classes, name='classes'),
    path('movie/', views.movie, name='movie'),
    path('gallery/', views.gallery, name='gallery'),
    path('order_form/', views.order_form, name='order_form'),
    path('sales/', views.sales, name='sales'),
    
    # Detail views
    path('details_s/<int:sword_img_id>/', views.details_s, name='details_s'),
    path('details_h/<int:hotel_id>/', views.details_h, name='details_h'),
    path('details_sales/<int:sword_sales_id>/', views.details_sales, name='details_sales'),
    
    # Supabase Blog URLs (replaces old blog)
    path('blog/', simple_views.simple_blog_list, name='simple_blog_list'),
    path('blog/<slug:slug>/', simple_views.simple_blog_detail, name='simple_blog_detail'),
    path('blog/category/<slug:slug>/', simple_views.simple_blog_category, name='simple_blog_category'),
    path('blog/tag/<slug:slug>/', simple_views.simple_blog_tag, name='simple_blog_tag'),
    path('blog/search/', simple_views.simple_blog_search, name='simple_blog_search'),
    
    # Legacy blog redirect (for backward compatibility)
    path('old-blog/', simple_views.blog_redirect, name='blog_redirect'),
]
