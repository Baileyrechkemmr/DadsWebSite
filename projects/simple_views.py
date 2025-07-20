"""
Simple, clean views for the AWS blog using PostgreSQL + S3
Much simpler than the DynamoDB approach
"""

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.utils import timezone
from .simple_aws_models import SimpleBlogPost, BlogCategory, BlogTag


def simple_blog_list(request):
    """
    Display published blog posts with pagination
    """
    # Get only published posts
    posts = SimpleBlogPost.objects.filter(
        status='published',
        publish_date__lte=timezone.now()
    ).select_related('category', 'author').prefetch_related('tags')
    
    # Handle category filtering
    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    # Handle tag filtering
    tag_slug = request.GET.get('tag')
    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)
    
    # Handle search
    search_query = request.GET.get('search')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        ).distinct()
    
    # Pagination
    paginator = Paginator(posts, 10)  # 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories and tags for sidebar
    categories = BlogCategory.objects.all()
    popular_tags = BlogTag.objects.filter(
        simpleblogpost__status='published'
    ).distinct()[:10]
    
    context = {
        'posts': page_obj,
        'categories': categories,
        'popular_tags': popular_tags,
        'search_query': search_query,
        'current_category': category_slug,
        'current_tag': tag_slug,
        'page_obj': page_obj,
    }
    
    return render(request, 'projects/simple_blog_list.html', context)


def simple_blog_detail(request, slug):
    """
    Display a single blog post
    """
    post = get_object_or_404(
        SimpleBlogPost.objects.select_related('category', 'author').prefetch_related('tags'),
        slug=slug
    )
    
    # Check if post should be visible
    if not post.is_published and not request.user.is_staff:
        raise Http404("Blog post not found")
    
    # Increment view count (only for published posts and non-staff users)
    if post.is_published and not request.user.is_staff:
        post.increment_view_count()
    
    # Get related posts (same category, excluding current post)
    related_posts = SimpleBlogPost.objects.filter(
        status='published',
        publish_date__lte=timezone.now(),
        category=post.category
    ).exclude(id=post.id)[:3]
    
    # Get comments if enabled
    comments = []
    if post.allow_comments:
        comments = post.comments.filter(is_approved=True).order_by('created_date')
    
    context = {
        'post': post,
        'related_posts': related_posts,
        'comments': comments,
    }
    
    return render(request, 'projects/simple_blog_detail.html', context)


def simple_blog_category(request, slug):
    """
    Display posts from a specific category
    """
    category = get_object_or_404(BlogCategory, slug=slug)
    
    posts = SimpleBlogPost.objects.filter(
        status='published',
        publish_date__lte=timezone.now(),
        category=category
    ).select_related('author').prefetch_related('tags')
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'posts': page_obj,
        'category': category,
        'page_obj': page_obj,
    }
    
    return render(request, 'projects/simple_blog_category.html', context)


def simple_blog_tag(request, slug):
    """
    Display posts with a specific tag
    """
    tag = get_object_or_404(BlogTag, slug=slug)
    
    posts = SimpleBlogPost.objects.filter(
        status='published',
        publish_date__lte=timezone.now(),
        tags=tag
    ).select_related('category', 'author').prefetch_related('tags')
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'posts': page_obj,
        'tag': tag,
        'page_obj': page_obj,
    }
    
    return render(request, 'projects/simple_blog_tag.html', context)


def simple_blog_search(request):
    """
    Search blog posts
    """
    search_query = request.GET.get('q', '').strip()
    posts = []
    
    if search_query:
        posts = SimpleBlogPost.objects.filter(
            status='published',
            publish_date__lte=timezone.now()
        ).filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).select_related('category', 'author').prefetch_related('tags').distinct()
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'posts': page_obj,
        'search_query': search_query,
        'page_obj': page_obj,
    }
    
    return render(request, 'projects/simple_blog_search.html', context)


# Compatibility redirect for old blog URL
def blog_redirect(request):
    """
    Redirect old blog URL to new simple blog
    """
    from django.shortcuts import redirect
    return redirect('simple_blog_list')