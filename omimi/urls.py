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
import projects
import projects.views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', projects.views.home, name='home'),
    path('about/', projects.views.about, name='about'),
    path('classes/', projects.views.classes, name='classes'),
    path('blog/', projects.views.blog, name='blog'),
    path('movie/', projects.views.movie, name='movie'),
    path('gallery/', projects.views.gallery, name='gallery'),
    path('details_s/<int:sword_img_id>',projects.views.details_s, name='details_s'),
    path('order_form/', projects.views.order_form, name='order_form'),
    path('details_h/<int:hotel_id>', projects.views.details_h, name='details_h'),
    path('sales/', projects.views.sales, name='sales'),
    path('details_sales/<int:sword_sales_id>',projects.views.details_sales, name='details_sales'),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    path("ckeditor5/", include('django_ckeditor_5.urls'), name="ck_editor_5_upload_file"),
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
