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
2.  **Publish**: Posts titles and links to X (Twitter) using headless Playwright automation, and to LinkedIn.

It is designed to run on AWS Lambda, scheduled via EventBridge, using DynamoDB for storage.

# Architecture

-   **CDK Stack**: Infrastructure as Code defined in `cdk/`. Creates:
    -   **DynamoDB Tables**: `RSSContent` (articles) and `FeedConfigurations` (settings).
    -   **S3 Bucket**: `TwitterStateBucket` (securely stores Playwright cookies).
    -   **Lambda Functions**: Playwright-compatible Docker Python functions for Fetching and Publishing.
    -   **EventBridge Rules**: Schedules Fetch (daily) and Publish (every 2 hours).
-   **SSM Parameter Store**: Securely stores LinkedIn credentials. (Twitter API keys are no longer used).

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
  urls:
    - https://simpleit.rocks/feed
  hashtags: '#TechTutorials'
  min_date: '2025-01-01' # Optional: Ignore articles older than this date
```
*(Note: Twitter API keys are no longer required in feeds.yml)*

## Credentials
-   **X (Twitter)**: Authentication is handled via session cookies to bypass API fees. You must generate a `twitter_state.json` file and upload it to your S3 `TwitterStateBucket`.
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

## X (Twitter) Authentication State
Since the bot uses Playwright to mimic a real user, it needs your session cookies.
1. Log into X.com on your local browser.
2. Open Developer Tools -> Application -> Cookies, and copy the `auth_token` and `ct0` values.
3. Run the state generator script:
```bash
python management/create_state_from_cookies.py --auth_token "YOUR_AUTH_TOKEN" --ct0 "YOUR_CT0_VALUE"
```
4. Upload the generated `twitter_state.json` to your CDK-created S3 bucket:
```bash
aws s3 cp twitter_state.json s3://<YOUR_TWITTER_STATE_BUCKET_NAME>/twitter_state.json
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
