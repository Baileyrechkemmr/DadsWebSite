"""
AWS DynamoDB service for blog post storage.
This service layer handles blog posts in DynamoDB while maintaining Django compatibility.
"""

import boto3
import json
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Optional
from django.conf import settings
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)


class DynamoDBBlogService:
    """Service for managing blog posts in DynamoDB"""
    
    def __init__(self):
        """Initialize DynamoDB client and table"""
        self.dynamodb = boto3.resource(
            'dynamodb',
            region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1'),
            aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
            aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
        )
        self.table_name = getattr(settings, 'DYNAMODB_BLOG_TABLE', 'omimi-blog-posts')
        self.table = None
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """Create DynamoDB table if it doesn't exist"""
        try:
            # Try to get the table first
            self.table = self.dynamodb.Table(self.table_name)
            self.table.load()  # This will raise an exception if table doesn't exist
            logger.info(f"Using existing DynamoDB table: {self.table_name}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.info(f"Creating DynamoDB table: {self.table_name}")
                self._create_table()
            else:
                logger.error(f"Error accessing DynamoDB table: {e}")
                raise
    
    def _create_table(self):
        """Create the blog posts table"""
        try:
            table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {
                        'AttributeName': 'blog_id',
                        'KeyType': 'HASH'  # Partition key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'blog_id',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'created_date',
                        'AttributeType': 'S'
                    }
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'DateIndex',
                        'KeySchema': [
                            {
                                'AttributeName': 'created_date',
                                'KeyType': 'HASH'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        },
                        'BillingMode': 'PAY_PER_REQUEST'
                    }
                ],
                BillingMode='PAY_PER_REQUEST'  # Serverless pricing
            )
            
            # Wait for table to be created
            table.wait_until_exists()
            self.table = table
            logger.info(f"Successfully created DynamoDB table: {self.table_name}")
            
        except ClientError as e:
            logger.error(f"Error creating DynamoDB table: {e}")
            raise
    
    def create_blog_post(self, title: str, content: str, images: List[str] = None, 
                        tags: List[str] = None) -> str:
        """Create a new blog post"""
        blog_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        item = {
            'blog_id': blog_id,
            'title': title,
            'content': content,
            'images': images or [],
            'tags': tags or [],
            'created_date': now.isoformat(),
            'updated_date': now.isoformat(),
            'published': True,
            'view_count': 0
        }
        
        try:
            self.table.put_item(Item=item)
            logger.info(f"Created blog post: {blog_id}")
            return blog_id
        except ClientError as e:
            logger.error(f"Error creating blog post: {e}")
            raise
    
    def get_blog_post(self, blog_id: str) -> Optional[Dict]:
        """Get a specific blog post by ID"""
        try:
            response = self.table.get_item(Key={'blog_id': blog_id})
            return response.get('Item')
        except ClientError as e:
            logger.error(f"Error getting blog post {blog_id}: {e}")
            return None
    
    def get_all_blog_posts(self, limit: int = 50) -> List[Dict]:
        """Get all blog posts, ordered by creation date (newest first)"""
        try:
            # Use the DateIndex to get posts ordered by date
            response = self.table.scan(
                Limit=limit,
                ScanFilter={
                    'published': {
                        'AttributeValueList': [True],
                        'ComparisonOperator': 'EQ'
                    }
                }
            )
            
            # Sort by created_date in Python (DynamoDB scan doesn't guarantee order)
            items = response.get('Items', [])
            items.sort(key=lambda x: x.get('created_date', ''), reverse=True)
            
            return items
        except ClientError as e:
            logger.error(f"Error getting blog posts: {e}")
            return []
    
    def update_blog_post(self, blog_id: str, **kwargs) -> bool:
        """Update a blog post"""
        if not kwargs:
            return False
            
        # Build update expression
        update_expression = "SET updated_date = :updated_date"
        expression_values = {':updated_date': datetime.now(timezone.utc).isoformat()}
        
        for key, value in kwargs.items():
            if key in ['title', 'content', 'images', 'tags', 'published']:
                update_expression += f", {key} = :{key}"
                expression_values[f":{key}"] = value
        
        try:
            self.table.update_item(
                Key={'blog_id': blog_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values
            )
            logger.info(f"Updated blog post: {blog_id}")
            return True
        except ClientError as e:
            logger.error(f"Error updating blog post {blog_id}: {e}")
            return False
    
    def delete_blog_post(self, blog_id: str) -> bool:
        """Delete a blog post"""
        try:
            self.table.delete_item(Key={'blog_id': blog_id})
            logger.info(f"Deleted blog post: {blog_id}")
            return True
        except ClientError as e:
            logger.error(f"Error deleting blog post {blog_id}: {e}")
            return False
    
    def increment_view_count(self, blog_id: str):
        """Increment the view count for a blog post"""
        try:
            self.table.update_item(
                Key={'blog_id': blog_id},
                UpdateExpression="ADD view_count :inc",
                ExpressionAttributeValues={':inc': 1}
            )
        except ClientError as e:
            logger.error(f"Error incrementing view count for {blog_id}: {e}")
    
    def search_blog_posts(self, search_term: str, limit: int = 20) -> List[Dict]:
        """Search blog posts by title or content (basic implementation)"""
        try:
            # Note: This is a basic search. For production, consider AWS OpenSearch
            response = self.table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr('title').contains(search_term) |
                               boto3.dynamodb.conditions.Attr('content').contains(search_term),
                Limit=limit
            )
            
            items = response.get('Items', [])
            items.sort(key=lambda x: x.get('created_date', ''), reverse=True)
            
            return items
        except ClientError as e:
            logger.error(f"Error searching blog posts: {e}")
            return []


# Singleton instance
blog_service = DynamoDBBlogService()