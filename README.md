# Publish Feed (Serverless Edition)

A publisher of articles from websites RSS feeds to Bluesky and LinkedIn, powered by AWS Lambda and DynamoDB.

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
2.  **Publish**: Posts titles and links to Bluesky using the official `atproto` SDK, and to LinkedIn.

On Bluesky, posts include **clickable hashtags** (rendered as AT Protocol tag facets) and a **link preview card** (an `app.bsky.embed.external` embed built from the article's OpenGraph metadata). Because the link lives in the preview card rather than inline text, the article URL does not count against Bluesky's 300-character limit.

It is designed to run on AWS Lambda, scheduled via EventBridge, using DynamoDB for storage and SSM Parameter Store for credentials.

# Architecture

-   **CDK Stack**: Infrastructure as Code defined in `cdk/`. Creates:
    -   **DynamoDB Tables**: `RSSContent` (articles) and `FeedConfigurations` (settings).
    -   **Lambda Functions**: Docker Python functions (`public.ecr.aws/lambda/python:3.11`) for Fetching and Publishing.
    -   **EventBridge Rules**: Schedules Fetch (daily) and Publish (every 2 hours).
-   **SSM Parameter Store**: Securely stores Bluesky, LinkedIn, and OpenAI credentials.

# Installation & Deployment

## Prerequisites
1.  **AWS Credentials**: Ensure your terminal has valid AWS credentials (`aws configure`).
2.  **CDK Installed**: `npm install -g aws-cdk`.
3.  **Docker**: Must be running (for building Lambda container images).

## Deploying the Stack

1.  **Install Python Dependencies**:
    ```bash
    pip install -r publishfeed/cdk/requirements.txt
    pip install boto3 pyyaml # For the sync script
    ```

2.  **Deploy Infrastructure**:
    ```bash
    cd cdk
    cdk bootstrap # (If first time using CDK in this region)
    cdk deploy
    ```
    **Important**: Note the Outputs `RssFeedStack.RSSContentTableName` and `RssFeedStack.FeedConfigurationsTableName`. You will need them.

# Configuration

## Feeds
Customize `feeds.yml.skel` and save it as `feeds.yml`:

```bash
cp publishfeed/feeds.yml.skel publishfeed/feeds.yml
```

Example `feeds.yml`:
```yaml
TechnologyFeeds: # Feed ID
  bluesky:
    handle: 'your.handle.bsky.social'
    password: 'your-app-password'
  urls:
    - https://cncf.io/blog/feed
  hashtags: '#TechTutorials'
  min_date: '2025-01-01' # Optional: Ignore articles older than this date
```

## Credentials
-   **Bluesky**: Defined inside `feeds.yml` under the `bluesky` section.
-   **LinkedIn**: Defined in `ln_credentials.json` (optional).
-   **OpenAI**: Defined in `openai_key.txt` (optional, for summaries).

## LinkedIn API Version
LinkedIn's versioned REST API requires a `LinkedIn-Version` header in `YYYYMM` format, and each version is only active for about 12 months. An expired version causes posts to fail with `HTTP 426 NONEXISTENT_VERSION`.

The version is configurable in [config.py](publishfeed/config.py) via the `LINKEDIN_API_VERSION` setting (default `202605`) and can be overridden without a code change by setting the `LINKEDIN_API_VERSION` environment variable on the `PublishFeedFunction` Lambda. **Bump this periodically** to a currently-active version to keep LinkedIn posting working.

# Management

## Syncing Configuration
Whenever you edit `feeds.yml`, `ln_credentials.json`, or `openai_key.txt`, run the sync script to update DynamoDB and SSM:

```bash
# Replace <config_table_name> with your deployed FeedConfigurations table name
python publishfeed/management/sync_feeds.py --region us-east-1 --table-name <config_table_name>
```

## Local Verification
You can test posting to Bluesky locally by running the test script with environment variables:

```bash
BLUESKY_HANDLE="your.handle.bsky.social" BLUESKY_PASSWORD="your-app-password" python publishfeed/management/test_local_post.py
```

## Data Migration
If you have an existing SQLite database from the previous version, you can migrate it to DynamoDB:

```bash
# Usage: python publishfeed/management/migrate_db.py <path_to_db> <feed_id> --region <region> --table-name <rss_content_table_name>
python publishfeed/management/migrate_db.py databases/rss_TechnologyFeeds.db TechnologyFeeds --region us-east-1 --table-name RssFeedStack-RSSContent-XXXXX
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
