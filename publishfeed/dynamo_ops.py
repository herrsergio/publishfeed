import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
import random
from datetime import datetime

class DynamoDBOps:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.rss_table_name = os.environ.get('RSS_TABLE_NAME', 'RSSContent')
        self.config_table_name = os.environ.get('CONFIG_TABLE_NAME', 'FeedConfigurations')
        self.rss_table = self.dynamodb.Table(self.rss_table_name)
        self.config_table = self.dynamodb.Table(self.config_table_name)

    def batch_write_rss_items(self, items):
        """
        Write multiple RSS items to the database.
        Items should be a list of dicts.
        """
        if not items:
            return
            
        print(f"DynamoDB: Writing batch of {len(items)} items...")
        try:
            with self.rss_table.batch_writer() as batch:
                for item in items:
                    # Ensure status is set
                    if 'status' not in item:
                        item['status'] = 'unpublished'
                    batch.put_item(Item=item)
            print("DynamoDB: Batch write successful")
        except Exception as e:
            print(f"DynamoDB: Error in batch_write_rss_items: {e}")

    def check_rss_item_exists(self, url):
        """
        Check if an RSS item already exists by URL.
        """
        try:
            response = self.rss_table.get_item(Key={'url': url})
            exists = 'Item' in response
            # print(f"DynamoDB: Check exists {url} -> {exists}") # Verbose
            return exists
        except Exception as e:
            print(f"DynamoDB: Error checking item existence {url}: {e}")
            return False

    def get_random_unpublished_item(self, min_date=None):
        """
        Get a random unpublished item.
        Using the GSI StatusIndex.
        If min_date is provided (YYYY-MM-DD), filter items added after that date.
        """
        key_condition = Key('status').eq('unpublished')
        if min_date:
            key_condition = key_condition & Key('dateAdded').gt(min_date)

        response = self.rss_table.query(
            IndexName='StatusIndex',
            KeyConditionExpression=key_condition,
            Limit=50 # limit to avoid scanning too many if simpler
        )
        items = response.get('Items', [])
        if not items:
            return None
        return random.choice(items)

    def mark_as_published(self, url):
        """
        Update the status of an item to published.
        """
        self.rss_table.update_item(
            Key={'url': url},
            UpdateExpression="set #s = :s",
            ExpressionAttributeNames={'#s': 'status'},
            ExpressionAttributeValues={':s': 'published'}
        )

    def get_feed_config(self, feed_id):
        """
        Get configuration for a specific feed.
        """
        response = self.config_table.get_item(Key={'feed_id': feed_id})
        return response.get('Item')
