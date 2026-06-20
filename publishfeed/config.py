import os

# Bluesky has a 300 character limit
POST_MAX_LENGTH = 300

# LinkedIn versioned APIs use a YYYYMM header. LinkedIn keeps each version
# active for ~12 months, so this must be bumped periodically (an expired
# version returns HTTP 426 NONEXISTENT_VERSION). Override via env var.
LINKEDIN_API_VERSION = os.environ.get("LINKEDIN_API_VERSION", "202605")

#DB_TEST_URL = 'sqlite://' # in memory
DB_TEST_URL = 'sqlite:///home/ubuntu/publishfeed/publishfeed/databases/rss_TechnologyFeeds.db' # file 
