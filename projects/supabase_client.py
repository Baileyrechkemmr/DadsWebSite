"""
Supabase client configuration for Omimi blog.
Optional client for advanced features (auth, real-time, file storage)
"""

try:
    from supabase import create_client, Client
    from django.conf import settings
    import os
    
    # Get Supabase credentials from environment
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')
    
    # Create client if credentials are available
    if SUPABASE_URL and SUPABASE_KEY:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    else:
        supabase = None
        
except ImportError:
    # Supabase package not installed - that's OK, we're just using PostgreSQL
    supabase = None


def get_supabase_client():
    """
    Get the Supabase client instance.
    Returns None if not configured or package not installed.
    """
    return supabase
