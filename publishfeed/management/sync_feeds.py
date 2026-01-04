#!/usr/bin/env python
import os
import sys
import yaml
import boto3
import json

# Add parent directory to path to import local modules if needed
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import argparse

def sync_feeds(region, table_name):
    """
    Reads feeds.yml and syncs config to DynamoDB and secrets to SSM.
    """
    feeds_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../feeds.yml'))
    
    if not os.path.exists(feeds_path):
        print(f"Error: {feeds_path} not found.")
        return

    with open(feeds_path, 'r') as f:
        feeds_data = yaml.safe_load(f)

    if region:
        dynamodb = boto3.resource('dynamodb', region_name=region)
        ssm = boto3.client('ssm', region_name=region)
    else:
        dynamodb = boto3.resource('dynamodb')
        ssm = boto3.client('ssm')
    
    # Use provided table name
    config_table = dynamodb.Table(table_name)
    
    # Verify table access
    try:
        config_table.load()
    except Exception as e:
        print(f"Error: Could not load table '{table_name}'. Make sure it exists and region is correct.")
        return

    print(f"Syncing feeds from {feeds_path} to region {region if region else 'default'}...")
    print(f"Targeting DynamoDB Table: {table_name}")

    for feed_id, data in feeds_data.items():
        print(f"Processing {feed_id}...")
        
        # 1. Update Config in DynamoDB
        # Exclude 'twitter' key from config stored in DB (it contains secrets)
        config_item = {
            'feed_id': feed_id,
            'urls': data.get('urls', []),
            'hashtags': data.get('hashtags', '')
        }
        
        config_table.put_item(Item=config_item)
        print(f"  - Config updated in DynamoDB table '{table_name}'")

        # 2. Update Secrets in SSM
        if 'twitter' in data:
            secrets = data['twitter']
            parameter_name = f"/rss-feed/{feed_id}/twitter_creds"
            
            ssm.put_parameter(
                Name=parameter_name,
                Value=json.dumps(secrets),
                Type='SecureString',
                Overwrite=True
            )
            print(f"  - Secrets updated in SSM at '{parameter_name}'")

    # 3. Update LinkedIn Secrets in SSM
    ln_creds_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../ln_credentials.json'))
    if os.path.exists(ln_creds_path):
        print("Processing LinkedIn credentials...")
        with open(ln_creds_path, 'r') as f:
            ln_creds = json.load(f)
            
        parameter_name = "/rss-feed/global/linkedin_creds"
        ssm.put_parameter(
            Name=parameter_name,
            Value=json.dumps(ln_creds),
            Type='SecureString',
            Overwrite=True
        )
        print(f"  - LinkedIn Secrets updated in SSM at '{parameter_name}'")
    else:
        print("Warning: ln_credentials.json not found. Skipping LinkedIn sync.")

    # 4. Update OpenAI Key in SSM
    openai_key_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../openai_key.txt'))
    if os.path.exists(openai_key_path):
        print("Processing OpenAI key...")
        with open(openai_key_path, 'r') as f:
            openai_key = f.read().strip()
            
        parameter_name = "/rss-feed/global/openai_key"
        ssm.put_parameter(
            Name=parameter_name,
            Value=openai_key,
            Type='SecureString',
            Overwrite=True
        )
        print(f"  - OpenAI Key updated in SSM at '{parameter_name}'")
    else:
        print("Warning: openai_key.txt not found. Skipping OpenAI key sync.")

    print("\nSync complete!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sync feeds.yml to DynamoDB and SSM')
    parser.add_argument('--region', help='AWS Region', default='us-east-1')
    parser.add_argument('--table-name', help='DynamoDB Config Table Name', required=True)
    args = parser.parse_args()
    
    sync_feeds(args.region, args.table_name)
