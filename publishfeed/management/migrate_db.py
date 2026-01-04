#!/usr/bin/env python
import sys
import os
import sqlite3
import boto3
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def migrate_db(sqlite_path, feed_id, region, table_name, dry_run=False):
    if not os.path.exists(sqlite_path):
        print(f"Error: Database file {sqlite_path} not found.")
        return

    print(f"Migrating {sqlite_path} for Feed ID: {feed_id} in region {region}...")
    print(f"Targeting DynamoDB Table: {table_name}")
    
    # Connect to SQLite
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    
    # Connect to DynamoDB
    if region:
        dynamodb = boto3.resource('dynamodb', region_name=region)
    else:
        dynamodb = boto3.resource('dynamodb')
        
    table = dynamodb.Table(table_name)
    
    # Check if table exists (simple check)
    try:
        table.load()
    except Exception as e:
        print(f"Error: Could not load table '{table_name}'. Make sure it exists and region is correct.")
        print(e)
        return

    # Read rows
    try:
        cursor.execute('SELECT url, title, "dateAdded", published FROM rsscontent')
        rows = cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"Error reading sqlite DB: {e}")
        return

    print(f"Found {len(rows)} items to migrate.")
    
    with table.batch_writer() as batch:
        for row in rows:
            url, title, date_added_str, published = row
            
            # Convert status
            status = 'published' if published else 'unpublished'
            
            # Ensure date is string ISO
            try:
                dt = datetime.fromisoformat(date_added_str)
                date_iso = dt.isoformat()
            except ValueError:
                date_iso = str(date_added_str)

            item = {
                'url': url,
                'title': title,
                'dateAdded': date_iso,
                'status': status,
                'feed_id': feed_id
            }
            
            if dry_run:
                print(f"[Dry Run] would write: {title} ({status})")
            else:
                batch.put_item(Item=item)

    print("Migration complete!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Migrate existing SQLite DB to DynamoDB')
    parser.add_argument('db_path', help='Path to SQLite .db file')
    parser.add_argument('feed_id', help='Feed ID (e.g., from feeds.yml key)')
    parser.add_argument('--region', help='AWS Region', default='us-east-1')
    parser.add_argument('--table-name', help='DynamoDB Table Name', required=True)
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing')
    
    args = parser.parse_args()
    
    migrate_db(args.db_path, args.feed_id, args.region, args.table_name, args.dry_run)
