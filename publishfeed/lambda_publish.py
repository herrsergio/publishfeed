import boto3
import os
from helpers import RSSContentHelper

def handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    config_table_name = os.environ.get('CONFIG_TABLE_NAME', 'FeedConfigurations')
    config_table = dynamodb.Table(config_table_name)
    
    response = config_table.scan()
    feeds = response.get('Items', [])
    
    print(f"Found {len(feeds)} feeds to process.")

    for feed in feeds:
        feed_id = feed['feed_id']
        print(f"Publishing feed: {feed_id}")
        try:
            helper = RSSContentHelper(feed_id)
            helper.tweet_rsscontent()
        except Exception as e:
            print(f"Error publishing feed {feed_id}: {e}")
        
    return {"statusCode": 200, "body": "Publish complete"}
