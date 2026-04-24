#!/usr/bin/env python
import os
import argparse
import boto3
from playwright.sync_api import sync_playwright

def sync_twitter_state(bucket_name, region):
    state_file = 'twitter_state.json'

    print("Launching browser for you to log in to X (Twitter)...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto('https://x.com/login')
        
        print("Please log in to your account.")
        print("Once you are fully logged in and see your timeline, press Enter here.")
        input("Press Enter when ready...")
        
        context.storage_state(path=state_file)
        print(f"State saved to {state_file}")
        browser.close()

    print(f"Uploading state to S3 bucket: {bucket_name} in region {region}...")
    s3 = boto3.client('s3', region_name=region)
    try:
        s3.upload_file(state_file, bucket_name, 'twitter_state.json')
        print("Upload successful!")
        
        # Clean up local file for security
        # os.remove(state_file)
        # print(f"Cleaned up local {state_file}")
    except Exception as e:
        print(f"Error uploading to S3: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Login to X and upload storage state to S3')
    parser.add_argument('--bucket', required=True, help='S3 Bucket name for Twitter state')
    parser.add_argument('--region', default='us-east-1', help='AWS Region')
    args = parser.parse_args()
    
    sync_twitter_state(args.bucket, args.region)
