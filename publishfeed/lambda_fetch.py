import boto3
import os
from helpers import FeedSetHelper

def handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    config_table_name = os.environ.get('CONFIG_TABLE_NAME', 'FeedConfigurations')
    config_table = dynamodb.Table(config_table_name)
    
    # Scan all feeds
    response = config_table.scan()
    feeds = response.get('Items', [])
    
    print(f"Found {len(feeds)} feeds to process.")

    for feed in feeds:
        feed_id = feed['feed_id']
        print(f"Fetching feed: {feed_id}")
        try:
            helper = FeedSetHelper(feed_id)
            helper.get_pages_from_feeds()
        except Exception as e:
            print(f"Error fetching feed {feed_id}: {e}")
        
    return {"statusCode": 200, "body": "Fetch complete"}
