"""
Updated views that use DynamoDB for blog posts while maintaining existing functionality.
These views replace the blog-related views in views.py
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from .aws_blog_service import blog_service
from .aws_models import DynamoDBBlogPost
import logging

logger = logging.getLogger(__name__)


@cache_page(60 * 5)  # Cache for 5 minutes
def aws_blog(request):
    """
    Display all published blog posts from DynamoDB
    """
    try:
        # Get all blog posts from DynamoDB
        blog_posts = DynamoDBBlogPost.objects.all()
        
        # Filter for published posts
        published_posts = [post for post in blog_posts if post.published]
        
        # Pagination
        paginator = Paginator(published_posts, 10)  # Show 10 posts per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # For each post, increment view count if not in preview mode
        if not request.GET.get('preview'):
            for post in page_obj:
                try:
                    blog_service.increment_view_count(post.blog_id)
                except Exception as e:
                    logger.warning(f"Could not increment view count for {post.blog_id}: {e}")
        
        context = {
            'blogs': page_obj,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
        }
        
        return render(request, 'projects/aws_blog.html', context)
        
    except Exception as e:
        logger.error(f"Error loading blog posts: {e}")
        messages.error(request, "Sorry, there was an error loading the blog posts. Please try again later.")
        
        # Return empty context to prevent template errors
        context = {
            'blogs': [],
            'page_obj': None,
            'is_paginated': False,
        }
        return render(request, 'projects/aws_blog.html', context)


def aws_blog_detail(request, blog_id):
    """
    Display a single blog post from DynamoDB
    """
    try:
        blog_post = DynamoDBBlogPost.objects.get(pk=blog_id)
        
        if not blog_post.published and not request.user.is_staff:
            raise Http404("Blog post not found or not published")
        
        # Increment view count (unless it's a preview or the user is staff)
        if not request.GET.get('preview') and not request.user.is_staff:
            try:
                blog_service.increment_view_count(blog_id)
                # Update the object's view count for display
                blog_post.view_count += 1
            except Exception as e:
                logger.warning(f"Could not increment view count for {blog_id}: {e}")
        
        context = {
            'blog': blog_post,
            'blog_images': blog_post.image_list,  # List of image URLs
            'tags': blog_post.get_tags_list(),
        }
        
        return render(request, 'projects/aws_blog_detail.html', context)
        
    except Exception as e:
        logger.error(f"Error loading blog post {blog_id}: {e}")
        raise Http404("Blog post not found")


@require_http_methods(["GET"])
def aws_blog_search(request):
    """
    Search blog posts in DynamoDB
    """
    search_query = request.GET.get('q', '').strip()
    
    if not search_query:
        return redirect('aws_blog')
    
    try:
        # Search using the blog service
        search_results = blog_service.search_blog_posts(search_query, limit=50)
        
        # Convert DynamoDB results to Django model instances
        blog_posts = []
        for item in search_results:
            try:
                blog_post = DynamoDBBlogPost.objects._dynamo_to_django(item)
                if blog_post.published:  # Only show published posts
                    blog_posts.append(blog_post)
            except Exception as e:
                logger.warning(f"Error converting search result: {e}")
        
        # Pagination
        paginator = Paginator(blog_posts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'blogs': page_obj,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
            'search_query': search_query,
            'total_results': len(blog_posts),
        }
        
        return render(request, 'projects/aws_blog_search.html', context)
        
    except Exception as e:
        logger.error(f"Error searching blog posts: {e}")
        messages.error(request, "Sorry, there was an error searching the blog posts. Please try again later.")
        return redirect('aws_blog')


@require_http_methods(["GET"])
def aws_blog_by_tag(request, tag):
    """
    Display blog posts filtered by tag
    """
    try:
        # Get all blog posts
        all_posts = DynamoDBBlogPost.objects.all()
        
        # Filter by tag and published status
        tagged_posts = []
        for post in all_posts:
            if post.published and tag.lower() in [t.lower() for t in post.get_tags_list()]:
                tagged_posts.append(post)
        
        # Pagination
        paginator = Paginator(tagged_posts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'blogs': page_obj,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
            'tag': tag,
            'total_results': len(tagged_posts),
        }
        
        return render(request, 'projects/aws_blog_tag.html', context)
        
    except Exception as e:
        logger.error(f"Error loading blog posts for tag '{tag}': {e}")
        messages.error(request, "Sorry, there was an error loading the blog posts. Please try again later.")
        return redirect('aws_blog')


@require_http_methods(["GET"])
def aws_blog_api(request):
    """
    JSON API endpoint for blog posts (for AJAX requests)
    """
    try:
        limit = int(request.GET.get('limit', 10))
        offset = int(request.GET.get('offset', 0))
        
        # Get all published posts
        all_posts = DynamoDBBlogPost.objects.all()
        published_posts = [post for post in all_posts if post.published]
        
        # Apply pagination manually
        paginated_posts = published_posts[offset:offset + limit]
        
        # Convert to JSON-serializable format
        posts_data = []
        for post in paginated_posts:
            posts_data.append({
                'id': post.blog_id,
                'title': post.title,
                'content': post.stripped_content[:200] + '...' if len(post.stripped_content) > 200 else post.stripped_content,
                'created_date': post.created_date.isoformat() if post.created_date else None,
                'tags': post.get_tags_list(),
                'image_urls': post.image_list,
                'view_count': post.view_count,
            })
        
        return JsonResponse({
            'posts': posts_data,
            'total': len(published_posts),
            'has_more': offset + limit < len(published_posts),
        })
        
    except Exception as e:
        logger.error(f"Error in blog API: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


def get_popular_tags(limit=10):
    """
    Helper function to get popular tags across all blog posts
    """
    try:
        all_posts = DynamoDBBlogPost.objects.all()
        tag_counts = {}
        
        for post in all_posts:
            if post.published:
                for tag in post.get_tags_list():
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Sort by count and return top tags
        popular_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [tag for tag, count in popular_tags]
        
    except Exception as e:
        logger.error(f"Error getting popular tags: {e}")
        return []


def aws_blog_stats(request):
    """
    Display blog statistics (for admin/staff users)
    """
    if not request.user.is_staff:
        raise Http404("Not found")
    
    try:
        all_posts = DynamoDBBlogPost.objects.all()
        
        published_count = sum(1 for post in all_posts if post.published)
        draft_count = sum(1 for post in all_posts if not post.published)
        total_views = sum(post.view_count for post in all_posts)
        
        popular_tags = get_popular_tags(20)
        
        # Get recent posts
        recent_posts = sorted(all_posts, key=lambda x: x.created_date or datetime.min, reverse=True)[:10]
        
        context = {
            'published_count': published_count,
            'draft_count': draft_count,
            'total_posts': len(all_posts),
            'total_views': total_views,
            'popular_tags': popular_tags,
            'recent_posts': recent_posts,
        }
        
        return render(request, 'projects/aws_blog_stats.html', context)
        
    except Exception as e:
        logger.error(f"Error loading blog stats: {e}")
        messages.error(request, "Error loading blog statistics.")
        return redirect('admin:index')


# Compatibility function to maintain existing blog view
def blog_compatibility(request):
    """
    Redirect old blog URLs to new AWS blog
    """
    return redirect('aws_blog')