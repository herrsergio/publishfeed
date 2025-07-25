import logging
import os
import random
import time
from urllib.parse import urlparse

import newspaper
import openai
import requests
from bs4 import BeautifulSoup
from newspaper import Config, settings


def load_openai_key():
    """Load OpenAI API key from file or environment variable."""
    key_file_path = os.path.join(os.path.dirname(__file__), "openai_key.txt")

    if os.path.exists(key_file_path):
        with open(key_file_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    # Fallback to environment variable
    return os.environ.get("OPENAI_KEY")


openai.api_key = load_openai_key()


def _extract_with_advanced_requests(url):
    """Advanced fallback extraction with sophisticated bot evasion."""
    strategies = [
        # Strategy 1: Simulate coming from Google
        {
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.google.com/",
                "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "cross-site",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0",
            },
            "delay": random.uniform(2, 4),
        },
        # Strategy 2: Simulate coming from social media
        {
            "headers": {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://twitter.com/",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "cross-site",
                "Upgrade-Insecure-Requests": "1",
            },
            "delay": random.uniform(1, 3),
        },
        # Strategy 3: Mobile browser simulation
        {
            "headers": {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.google.com/",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "cross-site",
            },
            "delay": random.uniform(1.5, 3.5),
        },
        # Strategy 4: Firefox with different approach
        {
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://duckduckgo.com/",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "cross-site",
                "Upgrade-Insecure-Requests": "1",
            },
            "delay": random.uniform(2, 5),
        },
    ]

    for i, strategy in enumerate(strategies):
        try:
            logging.info("Trying advanced request strategy %d", i + 1)

            # Random delay to appear human
            time.sleep(strategy["delay"])

            session = requests.Session()

            # First, visit the homepage to get cookies
            parsed_url = urlparse(url)
            homepage = f"{parsed_url.scheme}://{parsed_url.netloc}"

            try:
                session.get(homepage, headers=strategy["headers"], timeout=10)
                time.sleep(random.uniform(0.5, 1.5))
            except:
                pass  # Continue even if homepage visit fails

            # Now get the actual page
            response = session.get(
                url, headers=strategy["headers"], timeout=20, allow_redirects=True
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Remove unwanted elements
            for element in soup(
                [
                    "script",
                    "style",
                    "nav",
                    "header",
                    "footer",
                    "aside",
                    "iframe",
                    "noscript",
                ]
            ):
                element.decompose()

            # Try to find main content areas
            content_selectors = [
                "article",
                '[role="main"]',
                "main",
                ".content",
                ".post-content",
                ".entry-content",
                ".article-content",
                ".post-body",
                ".story-body",
                ".post",
                ".entry",
                ".article",
                ".blog-post",
                ".single-post",
            ]

            text = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    text = " ".join([elem.get_text(strip=True) for elem in elements])
                    if len(text) > 200:
                        break

            # Fallback to body if no specific content found
            if not text or len(text) < 200:
                body = soup.find("body")
                if body:
                    text = body.get_text(strip=True)

            # Clean up the text
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            text = " ".join(lines)

            if len(text) > 100:
                logging.info("Successfully extracted with advanced strategy %d", i + 1)
                return text

        except Exception as e:
            logging.warning("Advanced strategy %d failed: %s", i + 1, str(e))
            continue

    return ""


def _extract_with_requests(url):
    """Fallback extraction using requests and BeautifulSoup."""
    return _extract_with_advanced_requests(url)


def extract_article_text(url):
    """Extract article text from URL with multiple fallback strategies."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    ]

    # First try newspaper with different user agents
    for i, user_agent in enumerate(user_agents):
        try:
            config = Config()
            config.browser_user_agent = user_agent
            config.request_timeout = 10
            config.number_threads = 1

            article = newspaper.Article(url, config=config)
            article.download()
            article.parse()

            if article.text and len(article.text.strip()) > 100:
                logging.info(
                    "Successfully extracted article with newspaper (user agent %d)",
                    i + 1,
                )
                return article.text

            logging.warning("Article text too short or empty with user agent %d", i + 1)

        except Exception as e:
            logging.warning(
                "Failed to extract article with user agent %d: %s", i + 1, str(e)
            )
            continue

    # Fallback to advanced requests + BeautifulSoup
    logging.info("Trying advanced requests fallback for URL: %s", url)
    text = _extract_with_requests(url)
    if text:
        logging.info("Successfully extracted article with advanced requests fallback")
        return text

    # Final fallback: Try with minimal curl-like request
    logging.info("Trying minimal curl-like request for URL: %s", url)
    try:
        response = requests.get(
            url, headers={"User-Agent": "curl/7.68.0"}, timeout=10, allow_redirects=True
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            text = soup.get_text(strip=True)
            if len(text) > 100:
                logging.info("Successfully extracted with curl-like request")
                return text
    except Exception as e:
        logging.warning("Curl-like request failed: %s", str(e))

    logging.error("All extraction attempts failed for URL: %s", url)
    return ""


def extract_article_summary(url):
    """Extract article summary from URL with multiple fallback strategies."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    ]

    # First try newspaper with different user agents
    for i, user_agent in enumerate(user_agents):
        try:
            settings.MAX_SUMMARY_SENT = 3
            config = Config()
            config.browser_user_agent = user_agent
            config.request_timeout = 10
            config.number_threads = 1

            article = newspaper.Article(url, config=config)
            article.download()
            article.parse()
            article.nlp()

            if article.summary and len(article.summary.strip()) > 50:
                logging.info(
                    "Successfully extracted summary with newspaper (user agent %d)",
                    i + 1,
                )
                return article.summary

            logging.warning("Summary too short or empty with user agent %d", i + 1)

        except Exception as e:
            logging.warning(
                "Failed to extract summary with user agent %d: %s", i + 1, str(e)
            )
            continue

    # Fallback: extract full text and create summary from first few sentences
    logging.info("Trying advanced text extraction fallback for summary")
    text = _extract_with_requests(url)
    if text:
        # Create a simple summary from first 3 sentences
        sentences = text.split(". ")[:3]
        summary = ". ".join(sentences)
        if len(summary) > 50:
            logging.info("Successfully created summary from extracted text")
            return summary

    # Final fallback for summary
    logging.info("Trying minimal request for summary")
    try:
        response = requests.get(
            url, headers={"User-Agent": "curl/7.68.0"}, timeout=10, allow_redirects=True
        )
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            text = soup.get_text(strip=True)
            if len(text) > 100:
                sentences = text.split(". ")[:3]
                summary = ". ".join(sentences)
                if len(summary) > 50:
                    logging.info("Successfully created summary with minimal request")
                    return summary
    except Exception as e:
        logging.warning("Minimal request for summary failed: %s", str(e))

    logging.error("All summary extraction attempts failed for URL: %s", url)
    return ""


def summarize_text(text, max_tokens=250):
    """Summarize article text for social media with CTAs, emojis, and hashtags."""
    if not text:
        return ""

    try:
        prompt = """Create an engaging social media post (max 250 characters) from this article. 

REQUIREMENTS:
- Use a casual technical tone
- COULD include relevant emojis (2-4 emojis) if needed
- MUST include relevant hashtags based on the topic (e.g., #AI, #MachineLearning, #Tech, #Programming, #DataScience, #WebDev, #DevOps, #Cybersecurity, #Cloud, #Innovation)
- Keep it under 250 characters total
- These are not owned articles, so avoid using "our", "mine", "my"
- Make it engaging

FORMAT: [Summary] [Emojis] [CTA] [Hashtags]

Article content:
{text}"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": prompt.format(text=text),
                }
            ],
            temperature=0.8,
            max_tokens=max_tokens,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logging.error("LLM summarization failed: %s", str(e))
        return ""
