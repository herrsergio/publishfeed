import re
import requests
import feedparser
from datetime import datetime
from time import mktime

import config
from dynamo_ops import DynamoDBOps
from config_loader import ConfigLoader
from generate_hashtags_fuzzy import generate_hashtags_fuzzy
from llm_helpers import extract_article_text, summarize_text
from ln_oauth import ln_headers
from ln_post import ln_user_info, post_2_linkedin_new
from twitter import Twitter

class Helper:
    def __init__(self, feed_id):
        self.feed_id = feed_id
        self.config_loader = ConfigLoader()
        self.db_ops = DynamoDBOps()
        
        # Load config from DynamoDB
        self.feed_config = self.config_loader.load_feed_config(feed_id)
        if not self.feed_config:
            print(f"Warning: No configuration found for feed_id: {feed_id}")
            self.feed_config = {'urls': [], 'hashtags': ''}

class FeedSetHelper(Helper):
    def get_pages_from_feeds(self):
        urls = self.feed_config.get('urls', [])
        
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/114.0.0.0 Safari/537.36"
            )
        }
        
        new_items = []

        for url in urls:
            print(f"  Fetching URL: {url}")
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    parsed_feed = feedparser.parse(response.content)
                    print(f"    - Parsed {len(parsed_feed.entries)} entries")
                    
                    for entry in parsed_feed.entries:
                        item_url = entry.link
                        
                        # Check if exists in DynamoDB
                        if self.db_ops.check_rss_item_exists(item_url):
                            # print(f"      - Skipped (Exists): {item_url}")
                            continue
                            
                        item_title = entry.title
                        if "squid" in item_title.lower():
                            print(f"      - Skipped (Filter 'squid'): {item_title}")
                            continue

                        try:
                            # Parse date
                            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                                item_date = datetime.fromtimestamp(mktime(entry.published_parsed))
                            else:
                                item_date = datetime.now()

                            item = {
                                'url': item_url,
                                'title': item_title,
                                'dateAdded': item_date.isoformat(), # DynamoDB needs string
                                'status': 'unpublished',
                                'feed_id': self.feed_id # Track source feed
                            }
                            new_items.append(item)
                            print(f"      + New Item: {item_title}")
                            
                        except AttributeError as e:
                            print(f"      ! Error parsing entry: {e}")
                            continue
                else:
                    print(f"    ! Failed to fetch {url}. Status: {response.status_code}")
            except Exception as e:
                print(f"    ! Error fetching URL {url}: {e}")
                continue

        if new_items:
            print(f"  Saving {len(new_items)} new items for {self.feed_id}...")
            self.db_ops.batch_write_rss_items(new_items)
            print(f"  Saved {len(new_items)} items.")
        else:
            print(f"  No new items found for {self.feed_id} (or all were filtered/existed).")


class RSSContentHelper(Helper):
    def tweet_rsscontent(self):
        # 1. Get a random unpublished item
        min_date = self.feed_config.get('min_date')
        rsscontent = self.db_ops.get_random_unpublished_item(min_date)
        if not rsscontent:
            print("No unpublished items found.")
            return

        print(f"Processing: {rsscontent['title']}")

        # 2. Get Secrets (Twitter Keys)
        secrets = self.config_loader.load_secrets(self.feed_id)
        if not secrets:
            print(f"No secrets found for {self.feed_id}. Cannot post.")
            return
            
        # LinkedIn Token (Assume needed? The old code used ln_credentials.json)
        # For this migration, we are focusing on migrating the 'feeds.yml' secrets (Twitter).
        # But the code uses LinkedIn too. 
        # Ideally, we should store LinkedIn Token in SSM too. 
        # For now, let's assume the user has migrated LinkedIn logic effectively or we skip it if missing.
        # Actually, let's look at `ln_auth` again. It reads from file. 
        # We need to adapt this. 
        # For simplistic migration, I'll comment out LinkedIn part or assume token is passed.
        # Let's try to get LinkedIn token from SSM as well if we saved it there?
        # The current plan didn't explicitly say "migrate LinkedIn token to SSM" but it implied strict separation.
        # I'll stick to Twitter for now to match `feeds.yml` migration which was the request.
        # But wait, `tweet_rsscontent` in original files DOES post to LinkedIn.
        # I'll try to keep it functioning if I can.
        
        # ... (Continuing with Twitter logic) ...
        
        twitter = Twitter(**secrets)

        tweet_url = rsscontent['url']
        tweet_hashtag = self.feed_config.get('hashtags', '')
        
        # Generate hashtags
        the_hashtags = generate_hashtags_fuzzy(rsscontent['title'])
        content = rsscontent['title'] + "\n" + " ".join(list(the_hashtags))

        # OpenAI Summary
        article_text = extract_article_text(rsscontent['url'])
        tweet_text = ""
        
        if article_text:
            summary = summarize_text(article_text)
            
            # Post to LinkedIn 
            ln_secrets = self.config_loader.load_linkedin_secrets()
            if ln_secrets:
                try:
                    # We expect ln_secrets to have 'access_token'
                    # Or we might need to adapt ln_headers to accept the token directly
                    # The original ln_headers took access_token as arg.
                    access_token = ln_secrets.get('access_token')
                    if access_token:
                        linkedin_headers = ln_headers(access_token)
                        user_info = ln_user_info(linkedin_headers)
                        urn = user_info['id']
                        author = f"urn:li:person:{urn}"
                        api_url = "https://api.linkedin.com/rest/posts"
                        
                        post_2_linkedin_new(
                            rsscontent['title'],
                            rsscontent['url'],
                            summary,
                            author,
                            api_url,
                            linkedin_headers
                        )
                        print("Posted to LinkedIn.")
                    else:
                        print("LinkedIn access_token not found in secrets.")
                except Exception as e:
                    print(f"Error posting to LinkedIn: {e}")
            
            max_body_length = self._calculate_max_tweet_body_length(include_hashtags=False)
            if len(summary) > max_body_length:
                tweet_body = summary[:max_body_length].rsplit(" ", 1)[0]
            else:
                tweet_body = summary
            
            tweet_text = "{} \n\n{} ".format(tweet_body, tweet_url)
        else:
            # Fallback
            
            # Post to LinkedIn (Fallback content)
            ln_secrets = self.config_loader.load_linkedin_secrets()
            if ln_secrets:
                try:
                    access_token = ln_secrets.get('access_token')
                    if access_token:
                        linkedin_headers = ln_headers(access_token)
                        user_info = ln_user_info(linkedin_headers)
                        urn = user_info['id']
                        author = f"urn:li:person:{urn}"
                        api_url = "https://api.linkedin.com/rest/posts"
                        
                        post_2_linkedin_new(
                            rsscontent['title'],
                            rsscontent['url'],
                            content,
                            author,
                            api_url,
                            linkedin_headers
                        )
                        print("Posted to LinkedIn (Fallback).")
                except Exception as e:
                    print(f"Error posting to LinkedIn: {e}")

            body_length = self._calculate_max_tweet_body_length(include_hashtags=True)
            tweet_body = content[:body_length]
            tweet_text = "{} {} {}".format(tweet_body, tweet_url, tweet_hashtag)

        # Post to Twitter
        try:
            twitter.update_status(tweet_text)
            print("Posted to Twitter.")
            
            # Mark as published
            self.db_ops.mark_as_published(rsscontent['url'])
            
        except Exception as e:
            print(f"Error posting to Twitter: {e}")

    def _calculate_max_tweet_body_length(self, include_hashtags=True):
        """Calculate maximum length for tweet body considering URL and optional hashtags."""
        available_length = (
            config.TWEET_MAX_LENGTH - config.TWEET_URL_LENGTH - config.TWEET_IMG_LENGTH
        )
        if include_hashtags:
            # In new logic, hashtags is a string, not list? Old: len(self.data["hashtags"])
            # self.feed_config['hashtags'] is likely a string or list.
            ht = self.feed_config.get('hashtags', '')
            hashtag_length = len(ht)
            available_length -= hashtag_length
        return available_length - 2
