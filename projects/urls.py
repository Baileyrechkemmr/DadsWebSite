"""
URL patterns for the projects app with AWS blog integration.
"""

from django.urls import path
from . import views, aws_views

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
    
    # Legacy blog URL (redirects to AWS blog)
    path('blog/', aws_views.blog_compatibility, name='blog'),
    
    # AWS Blog URLs
    path('aws-blog/', aws_views.aws_blog, name='aws_blog'),
    path('aws-blog/<str:blog_id>/', aws_views.aws_blog_detail, name='aws_blog_detail'),
    path('aws-blog/search/', aws_views.aws_blog_search, name='aws_blog_search'),
    path('aws-blog/tag/<str:tag>/', aws_views.aws_blog_by_tag, name='aws_blog_by_tag'),
    path('aws-blog/api/posts/', aws_views.aws_blog_api, name='aws_blog_api'),
    path('aws-blog/admin/stats/', aws_views.aws_blog_stats, name='aws_blog_stats'),
]
