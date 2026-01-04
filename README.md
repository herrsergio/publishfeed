# Publish Feed (Serverless Edition)

A publisher of articles from websites RSS feeds to Twitter and LinkedIn, now powered by AWS Lambda and DynamoDB.

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-generate-toc again -->
**Table of Contents**

- [Overview](#overview)
- [Architecture](#architecture)
- [Installation & Deployment](#installation-&-deployment)
- [Configuration](#configuration)
    - [Feeds](#feeds)
    - [Credentials](#credentials)
- [Management](#management)
    - [Syncing Configuration](#syncing-configuration)
    - [Data Migration](#data-migration)
- [Development](#development)
- [License](#license)

<!-- markdown-toc end -->

# Overview

This app performs two main tasks:
1.  **Fetch**: Downloads RSS content from sources listed in `feeds.yml`.
2.  **Publish**: Posts titles and links to Twitter and LinkedIn.

It is designed to run on AWS Lambda, scheduled via EventBridge, using DynamoDB for storage.

# Architecture

-   **CDK Stack**: Infrastructure as Code defined in `cdk/`. Creates:
    -   **DynamoDB Tables**: `RSSContent` (articles) and `FeedConfigurations` (settings).
    -   **Lambda Functions**: Docker-based Python 3.12 functions for Fetching and Publishing.
    -   **EventBridge Rules**: Schedules Fetch (daily) and Publish (every 2 hours).
-   **SSM Parameter Store**: Securely stores Twitter and LinkedIn credentials.

# Installation & Deployment

## Prerequisites
1.  **AWS Credentials**: Ensure your terminal has valid AWS credentials (`aws configure`).
2.  **CDK Installed**: `npm install -g aws-cdk`.
3.  **Docker**: Must be running (for building Lambda images).

## Deploying the Stack

1.  **Install Python Dependencies**:
    ```bash
    pip install -r publishfeed/cdk/requirements.txt
    pip install boto3 pytaml # For the sync script
    ```

2.  **Deploy Infrastructure**:
    ```bash
    cd publishfeed/cdk
    cdk bootstrap # (If first time using CDK in this region)
    cdk deploy
    ```
    **Important**: Note the Outputs `RssFeedStack.RSSContentTableName` and `RssFeedStack.FeedConfigurationsTableName`. You will need them.

# Configuration

## Feeds
Customize `feeds.yml.skel` and save it as `feeds.yml`:

```bash
cd publishfeed
cp feeds.yml.skel feeds.yml
```

Example `feeds.yml`:
```yaml
TechnologyFeeds: # Feed ID
  twitter:
    consumer_key: 'XXXXXX'
    consumer_secret: 'XXXXXXX'
    access_key: 'XXXXXX'
    access_secret: 'XXXXXX'
  urls:
    - https://simpleit.rocks/feed
  hashtags: '#TechTutorials'
```

## Credentials
-   **Twitter**: Defined in `feeds.yml` under each feed ID.
-   **LinkedIn**: Defined in `ln_credentials.json` (optional).
-   **OpenAI**: Defined in `openai_key.txt` (optional, for summaries).

# Management

## Syncing Configuration
Whenever you edit `feeds.yml`, `ln_credentials.json` or `openai_key.txt`, run the sync script to update DynamoDB and SSM:

```bash
cd publishfeed
# Replace <config_table_name> with your deployed FeedConfigurations table name
python management/sync_feeds.py --region us-east-1 --table-name <config_table_name>
```

## Data Migration
If you have an existing SQLite database from the previous version, you can migrate it to DynamoDB:

```bash
cd publishfeed
# Usage: python management/migrate_db.py <path_to_db> <feed_id> --region <region> --table-name <rss_content_table_name>
python management/migrate_db.py databases/rss_TechnologyFeeds.db TechnologyFeeds --region us-east-1 --table-name RssFeedStack-RSSContent-XXXXX
```

# Development

To update the code:
1.  Modify the Python files in `publishfeed/publishfeed/`.
2.  Redeploy with CDK to rebuild the Docker image:
    ```bash
    cd cdk
    cdk deploy
    ```

# License

MIT Licensed.
