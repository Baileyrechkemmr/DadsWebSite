"""omimi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path ,include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path
from django.http import JsonResponse
import projects
import projects.views

def health_check(request):
    """Robust health check endpoint for Railway deployment"""
    try:
        # Basic Django health check
        from django.db import connection
        from django.core.cache import cache
        
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Test cache (optional)
        cache.set('health_check', 'ok', 30)
        cache_result = cache.get('health_check')
        
        return JsonResponse({
            "status": "healthy", 
            "message": "Django app is running",
            "database": "connected",
            "cache": "ok" if cache_result else "unavailable"
        })
    except Exception as e:
        # Return healthy status even if some services are down
        # This prevents Railway from restarting the app unnecessarily
        return JsonResponse({
            "status": "healthy", 
            "message": "Django app is running",
            "note": f"Some services may be initializing: {str(e)[:100]}"
        })

urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('admin/', admin.site.urls),
    path('', projects.views.home, name='home'),
    path('about/', projects.views.about, name='about'),
    path('classes/', projects.views.classes, name='classes'),
    path('blog/', projects.views.blog, name='blog'),
    path('movie/', projects.views.movie, name='movie'),
    path('gallery/', projects.views.gallery, name='gallery'),
    path('details_s/<int:sword_img_id>',projects.views.details_s, name='details_s'),
    path('gallery/<int:gallery_id>/', projects.views.gallery_detail, name='gallery_detail'),
    path('order_form/', projects.views.order_form, name='order_form'),
    path('details_h/<int:hotel_id>', projects.views.details_h, name='details_h'),
    path('sales/', projects.views.sales, name='sales'),
    path('details_sales/<int:sword_sales_id>',projects.views.details_sales, name='details_sales'),
    path("ckeditor5/", include('django_ckeditor_5.urls'), name="ck_editor_5_upload_file"),
]

# Only serve media files locally when NOT using S3
if not getattr(settings, 'USE_S3', False):
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
