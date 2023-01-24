from models import RSSContent, FeedSet
from twitter import Twitter
import yaml
import config
import feedparser
import re
from datetime import datetime
from time import mktime
from sqlalchemy.sql.expression import func
from ln_oauth import ln_auth, ln_headers
from ln_post import ln_user_info, post_2_linkedin, post_2_linkedin_legacy


class Helper:
    def __init__(self, session, data):
        self.session = session
        if (isinstance(data, dict)):
            self.data = data
        else:
            with open('/home/ubuntu/publishfeed/publishfeed/feeds.yml', 'r') as f:
                self.data = yaml.safe_load(f)[data]


class FeedSetHelper(Helper):

    def get_pages_from_feeds(self):
        feed = FeedSet(self.data)
        for url in feed.urls:
            parsed_feed = feedparser.parse(url)
            for entry in parsed_feed.entries:
                # if feed page not exist, add it as rsscontent
                q = self.session.query(RSSContent).filter_by(url=entry.link)
                exists = self.session.query(q.exists()).scalar()  # returns True or False
                if not exists:
                    item_title = entry.title
                    if "squid" in item_title.lower():
                        continue
                    item_url = entry.link  # .encode('utf-8')

                    item_date = datetime.fromtimestamp(mktime(entry.published_parsed))

                    item = RSSContent(url=item_url, title=item_title, dateAdded=item_date)
                    self.session.add(item)


class RSSContentHelper(Helper):

    def get_oldest_unpublished_rsscontent(self, session):
        # rsscontent = session.query(RSSContent).filter_by(published = 0).filter(RSSContent.dateAdded >
        # '2020-01-01').order_by(RSSContent.title).first()
        rsscontent = session.query(RSSContent).filter_by(published=0).filter(
            RSSContent.dateAdded > '2022-08-22').order_by(func.random()).first()
        return rsscontent

    def _calculate_tweet_length(self):
        tweet_net_length = config.TWEET_MAX_LENGTH - config.TWEET_URL_LENGTH - config.TWEET_IMG_LENGTH
        hashtag_length = len(self.data['hashtags'])
        body_length = tweet_net_length - hashtag_length
        return body_length

    def generate_hashtags(self, string, word_list):
        words = re.findall(r'\b\w+\b', string) # Get all words from the string
        hashtags = []
        for word in words:
            if word.lower() in word_list:
                hashtag = "#" + word.lower()
                hashtags.append(hashtag)
        return hashtags

    def tweet_rsscontent(self, rsscontent):
        ln_credentials = '/home/ubuntu/publishfeed/publishfeed/ln_credentials.json'
        linkedin_access_token = ln_auth(ln_credentials)  # Authenticate the API
        linkedin_headers = ln_headers(linkedin_access_token)  # Make the headers to attach to the API call.

        # Get user id to make a UGC post
        user_info = ln_user_info(linkedin_headers)
        urn = user_info['id']

        #Hashtags
        hashtag_list = ["agile", "amazon", "analytics", "api", "architecture", "aurora", "azure", "bigquery",
                        "blockchain", "brand", "cisco", "cncf", "coding", "compliance", "containers",
                        "customer", "data", "deployment", "digital", "docker", "ec2", "economy", "encryption",
                        "engineering", "experts", "fargate", "firewall", "fintech", "forrester", "future",
                        "gartner", "government", "google", "health", "healthcare", "ia", "iam", "india",
                        "infrastructure", "innovation", "jenkins", "kubernetes", "leadership", "location",
                        "linux", "logging", "management", "maturity", "microsoft", "microservices", "microservice",
                        "ml", "ml/ai", "mesh", "metaverse", "motivation", "microsoft", "partners", "pod",
                        "pods", "powerpoint", "productivity", "pipeline", "proxy", "rds", "robot", "robotics",
                        "s3", "sales", "salesforce", "science", "security", "scrum", "sre", "stateful", "stateless",
                        "strategy", "success", "terraform", "technology", "togaf", "transformation", "vmware"]

        the_hashtags = self.generate_hashtags(rsscontent.title, hashtag_list)
        content = rsscontent.title + " " + " ".join([x for x in the_hashtags])

        # UGC will replace shares over time.
        #api_url = 'https://api.linkedin.com/v2/ugcPosts'
        api_url = 'https://api.linkedin.com/v2/shares'
        author = f'urn:li:person:{urn}'
        #post_2_linkedin(rsscontent.title, rsscontent.url, rsscontent.title, author, api_url, linkedin_headers)
        post_2_linkedin_legacy(rsscontent.title, rsscontent.url, content, author, api_url, linkedin_headers)

        credentials = self.data['twitter']
        twitter = Twitter(**credentials)

        body_length = self._calculate_tweet_length()
        tweet_body = content[:body_length]
        tweet_url = rsscontent.url
        tweet_hashtag = self.data['hashtags']
        tweet_text = "{} {} {}".format(tweet_body, tweet_url, tweet_hashtag)
        twitter.update_status(tweet_text)
        rsscontent.published = True
        self.session.flush()
