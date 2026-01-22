import boto3
import os
from helpers import FeedSetHelper

import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info("Starting FetchFeedFunction")
    dynamodb = boto3.resource('dynamodb')
    config_table_name = os.environ.get('CONFIG_TABLE_NAME', 'FeedConfigurations')
    config_table = dynamodb.Table(config_table_name)
    
    # Scan all feeds
    logger.info(f"Scanning config table: {config_table_name}")
    response = config_table.scan()
    feeds = response.get('Items', [])
    
    logger.info(f"Found {len(feeds)} feeds to process.")

    for feed in feeds:
        feed_id = feed['feed_id']
        logger.info(f"Processing feed_id: {feed_id}")
        try:
            helper = FeedSetHelper(feed_id)
            helper.get_pages_from_feeds()
        except Exception as e:
            logger.error(f"Error processing feed {feed_id}: {e}", exc_info=True)
            
    logger.info("FetchFeedFunction complete")
    return {"statusCode": 200, "body": "Fetch complete"}
