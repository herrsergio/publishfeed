import re
from datetime import datetime
from time import mktime

import config
import feedparser
import requests
import yaml
from generate_hashtags_fuzzy import generate_hashtags_fuzzy
from llm_helpers import extract_article_text, summarize_text
from ln_oauth import ln_auth, ln_headers
from ln_post import ln_user_info, post_2_linkedin_new
from models import FeedSet, RSSContent
from sqlalchemy.sql.expression import func
from twitter import Twitter


class Helper:
    def __init__(self, session, data):
        self.session = session
        if isinstance(data, dict):
            self.data = data
        else:
            with open("/home/ubuntu/publishfeed/publishfeed/feeds.yml", "r") as f:
                self.data = yaml.safe_load(f)[data]


class FeedSetHelper(Helper):
    def get_pages_from_feeds(self):
        feed = FeedSet(self.data)
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/114.0.0.0 Safari/537.36"
            )
        }
        for url in feed.urls:
            # feedparser treats as an invalid XML media type and refuses to parse it
            # feedparser respects the Content-Type header to decide if the response is an XML feed.
            # When it sees text/plain, it assumes the content is just plain text and not a feed,
            # so it raises that error.
            # Overriding the Content-Type header by fetching the feed manually and
            # passing the raw content to feedparser
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                parsed_feed = feedparser.parse(url)
                for entry in parsed_feed.entries:
                    # if feed page not exist, add it as rsscontent
                    q = self.session.query(RSSContent).filter_by(url=entry.link)
                    exists = self.session.query(
                        q.exists()
                    ).scalar()  # returns True or False
                    if not exists:
                        item_title = entry.title
                        if "squid" in item_title.lower():
                            continue
                        item_url = entry.link  # .encode('utf-8')

                        try:
                            item_date = datetime.fromtimestamp(
                                mktime(entry.published_parsed)
                            )

                            item = RSSContent(
                                url=item_url, title=item_title, dateAdded=item_date
                            )
                            self.session.add(item)
                        except AttributeError:
                            print("The published_parsed attribute is not available")
                            continue
            else:
                continue


class RSSContentHelper(Helper):
    def get_oldest_unpublished_rsscontent(self, session):
        # rsscontent = session.query(RSSContent).filter_by(published = 0).filter(RSSContent.dateAdded >
        # '2020-01-01').order_by(RSSContent.title).first()
        rsscontent = (
            session.query(RSSContent)
            .filter_by(published=0)
            .filter(RSSContent.dateAdded > "2025-03-01")
            .order_by(func.random())
            .first()
        )
        return rsscontent

    def generate_hashtags(self, string, word_list):
        words = re.findall(r"\b\w+\b", string)  # Get all words from the string
        hashtags = []
        for word in words:
            if word.lower() in word_list:
                hashtag = "#" + word.lower()
                hashtags.append(hashtag)
        hashtags = list(dict.fromkeys(hashtags))  # Remove duplicates
        return hashtags

    def _calculate_max_tweet_body_length(self, include_hashtags=True):
        """Calculate maximum length for tweet body considering URL and optional hashtags."""
        available_length = (
            config.TWEET_MAX_LENGTH - config.TWEET_URL_LENGTH - config.TWEET_IMG_LENGTH
        )
        if include_hashtags:
            hashtag_length = len(self.data["hashtags"])
            available_length -= hashtag_length
        # Reserve 2 characters for spaces between body, URL, and hashtags
        return available_length - 2

    def tweet_rsscontent(self, rsscontent):
        ln_credentials = "/home/ubuntu/publishfeed/publishfeed/ln_credentials.json"
        linkedin_access_token = ln_auth(ln_credentials)  # Authenticate the API
        linkedin_headers = ln_headers(
            linkedin_access_token
        )  # Make the headers to attach to the API call.

        # Get user id to make a UGC post
        user_info = ln_user_info(linkedin_headers)
        urn = user_info["id"]

        the_hashtags = generate_hashtags_fuzzy(rsscontent.title)
        content = rsscontent.title + "\n" + " ".join(list(the_hashtags))

        api_url = "https://api.linkedin.com/rest/posts"
        author = f"urn:li:person:{urn}"

        credentials = self.data["twitter"]
        twitter = Twitter(**credentials)

        tweet_url = rsscontent.url
        tweet_hashtag = self.data["hashtags"]

        # Use OpenAI to generate a summary
        article_text = extract_article_text(rsscontent.url)
        if article_text:
            summary = summarize_text(article_text)
            post_2_linkedin_new(
                rsscontent.title,
                rsscontent.url,
                summary,
                author,
                api_url,
                linkedin_headers,
            )

            # For AI summary: don't add extra hashtags since summary already contains them
            # Calculate max length without additional hashtags
            max_body_length = self._calculate_max_tweet_body_length(
                include_hashtags=False
            )

            # Ensure the summary fits within Twitter limits
            if len(summary) > max_body_length:
                tweet_body = summary[:max_body_length].rsplit(" ", 1)[
                    0
                ]  # Cut at word boundary
            else:
                tweet_body = summary

            tweet_text = "{} {}".format(tweet_body, tweet_url)
        else:
            post_2_linkedin_new(
                rsscontent.title,
                rsscontent.url,
                content,
                author,
                api_url,
                linkedin_headers,
            )

            # For fallback: use original logic with hashtags
            body_length = self._calculate_max_tweet_body_length(include_hashtags=True)
            tweet_body = content[:body_length]
            tweet_text = "{} {} {}".format(tweet_body, tweet_url, tweet_hashtag)

        # Final safety check to ensure tweet doesn't exceed 280 characters
        if len(tweet_text) > config.TWEET_MAX_LENGTH:
            # Emergency truncation - this shouldn't happen with proper calculation
            tweet_text = tweet_text[: config.TWEET_MAX_LENGTH - 3] + "..."

        twitter.update_status(tweet_text)
        rsscontent.published = True
        self.session.flush()
